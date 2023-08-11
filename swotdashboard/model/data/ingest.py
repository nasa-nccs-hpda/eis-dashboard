import xarray as xr
import s3fs

# -----------------------------------------------------------------------------
# Ingest
# -----------------------------------------------------------------------------
class Ingest:

    def __init__(self, config):

        self.config = config

        self.s3 = s3fs.S3FileSystem(anon=True)

    # ------------------------------------------------------------------------
    # ingest
    # ------------------------------------------------------------------------
    def ingest(self):
        """_summary_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        ingestedData = {}

        for datasetName, filePath in self.config.items():

            if not filePath.endswith(".nc"):

                raise ValueError(f"File '{filePath}' is not a valid NetCDF file.")

            try:

                with self.s3.open(filePath, "rb") as file:

                    dataset = xr.open_dataset(file)

                    ingestedData[datasetName] = dataset

            except Exception as e:

                print(f"Error ingesting '{datasetName}' from '{filePath}': {e}")
        
        return ingestedData