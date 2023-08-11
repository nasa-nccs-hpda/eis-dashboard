from holoviews.streams import Stream, param


class ClickStream(Stream):
    """_summary_

    Args:
        Stream (_type_): _description_
    """
    lat = param.Number(default=0, bounds=(-90, 90))
    lon = param.Number(default=0, bounds=(-180, 180))
