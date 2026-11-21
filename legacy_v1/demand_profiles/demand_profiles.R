# ---- Libraries ----
library(ggplot2)
library(dplyr)
library(tidyr)
library(RColorBrewer)
library(grid)
library(gridExtra)
library(tools)

# ---- Main plotting function (saves PNG @ 300 dpi) ----
plot_single_benchmark <- function(
    csv_path,
    plot_title = NULL,
    base_color = "#30638e",
    width = 12,      # inches
    height = 12,     # inches
    dpi = 300,
    base_font_size = 16   # <-- NEW: global font size
) {
  # Read
  dat_raw <- read.csv(csv_path, check.names = TRUE, stringsAsFactors = FALSE)
  
  if (!"custom_id" %in% names(dat_raw)) {
    stop("The CSV must have a first column named 'custom_id'.")
  }
  
  # Keep only demand columns
  demand_cols <- setdiff(names(dat_raw), "custom_id")
  if (length(demand_cols) == 0) stop("No demand columns found (only 'custom_id' present).")
  
  # Expected demand order
  demand_order <- c("AS","CEc","CEe","CL","MCr",
                    "MCt","MCu","MS","QLl","QLq",
                    "SNs","KNa","KNc","KNf","KNn",
                    "KNs","AT","VO")
  
  present_demands <- intersect(demand_order, demand_cols)
  missing_in_file <- setdiff(demand_order, demand_cols)
  extra_in_file   <- setdiff(demand_cols, demand_order)
  demand_cols_final <- c(present_demands, sort(extra_in_file))
  
  # Clamp values to [0..5]
  dat_clean <- dat_raw |>
    mutate(across(all_of(demand_cols_final), \(x) suppressWarnings(as.integer(x)))) |>
    mutate(across(all_of(demand_cols_final), \(x) pmax(pmin(x, 5), 0)))
  
  # Long format
  df_long <- dat_clean |>
    pivot_longer(cols = all_of(demand_cols_final),
                 names_to = "Demand",
                 values_to = "value")
  
  # Count table
  df_counts <- df_long |>
    group_by(Demand, value) |>
    summarise(Freq = n(), .groups = "drop") |>
    complete(Demand, value = 0:5, fill = list(Freq = 0)) |>
    mutate(Demand = factor(Demand, levels = demand_cols_final))
  
  # Color gradient
  my_gradient <- colorRampPalette(c("white", base_color))(3)
  
  # Title
  if (is.null(plot_title)) {
    plot_title <- tools::file_path_sans_ext(basename(csv_path))
  }
  
  # Build plot
  p <- ggplot(df_counts, aes(x = Demand, y = value, fill = Freq)) +
    geom_tile(color = "white", size = 0.6) +
    geom_hline(yintercept = seq(0.5, 5.5, by = 1), color = "#66666E", size = 0.5) +
    scale_fill_gradientn(colors = my_gradient) +
    coord_polar(theta = "x", start = 0) +
    scale_y_continuous(breaks = 0:5, expand = c(0, 0)) +
    labs(title = plot_title, fill = "", x = "", y = "") +
    theme_minimal(base_size = base_font_size) +
    theme(
      axis.text.x  = element_text(size = base_font_size, vjust = 0.5, margin = margin(t = -5)),
      axis.text.y  = element_blank(),
      plot.title   = element_text(size = base_font_size + 4, face = "bold", hjust = 0.5),
      legend.text  = element_text(size = base_font_size - 2, colour = "black"),
      legend.title = element_blank(),
      panel.grid   = element_blank()
    )
  
  # Custom radial labels (bigger now)
  y_axis_df <- data.frame(x_val = 0.5, y = 0:5, label = 0:5)
  p <- p + geom_text(data = y_axis_df,
                     aes(x = x_val, y = y, label = label),
                     inherit.aes = FALSE,
                     fontface = "bold",
                     size = base_font_size * 0.6,
                     hjust = 1.2)
  
  # Save PNG @ 300 dpi
  out_prefix <- tools::file_path_sans_ext(basename(csv_path))
  out_file <- paste0(out_prefix, ".png")
  ggsave(filename = out_file, plot = p, width = width, height = height, dpi = dpi, units = "in")
  
  # Info
  if (length(missing_in_file)) {
    message("Missing expected demands (not in file): ", paste(missing_in_file, collapse = ", "))
  }
  if (length(extra_in_file)) {
    message("Extra columns treated as demands: ", paste(extra_in_file, collapse = ", "))
  }
  
  invisible(p)
}


# ---- Helper to process ALL CSVs in current directory ----
plot_all_benchmarks_in_dir <- function(
    pattern = "\\.csv$",
    base_color = "#30638e",
    width = 12,
    height = 12,
    dpi = 300
) {
  csvs <- list.files(pattern = pattern, ignore.case = TRUE)
  if (length(csvs) == 0) {
    message("No CSV files found in the current directory.")
    return(invisible(NULL))
  }
  for (csv in csvs) {
    message("Processing: ", csv)
    try({
      plot_single_benchmark(
        csv_path = csv,
        base_color = base_color,
        width = width,
        height = height,
        dpi = dpi
      )
    }, silent = TRUE)
  }
  invisible(csvs)
}

# ---- Run over all CSVs in the current directory ----
plot_all_benchmarks_in_dir()






