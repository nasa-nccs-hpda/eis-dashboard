import xarray as xr


# -----------------------------------------------------------------------------
# Preprocessing
# -----------------------------------------------------------------------------
class Preprocessing:
    def __init__(self, datasets, config):
        self.datasets = datasets
        self.config = config
        self.resample_frequency = self.config.resample_frequency

    # ------------------------------------------------------------------------
    # preprocess
    # ------------------------------------------------------------------------
    def preprocess(self):
        processed_data = {}
        names_and_paths = zip(self.config.data.paths, self.config.data.names)
        for dataset_name, subdatasets in self.config.data.paths:
            if dataset_name not in self.datasets:
                raise ValueError(f"Dataset '{dataset_name}' not found.")

            dataset = self.datasets[dataset_name]
            processed_subdatasets = {}

            for subdataset_name, resample_frequency in subdatasets.items():
                if subdataset_name not in dataset:
                    raise ValueError(
                        f"Subdataset '{subdataset_name}' not found in '{dataset_name}'.")

                subdataset = dataset[subdataset_name]
                resampled_data = subdataset.resample(
                    time=self.resample_frequency).mean()
                processed_subdatasets[subdataset_name] = resampled_data

            processed_data[dataset_name] = processed_subdatasets

        return processed_data
