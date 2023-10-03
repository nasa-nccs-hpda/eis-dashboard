from holoviews.streams import Stream, param


class PolygonDrawStream(Stream):
    """_summary_

    Args:
        Stream (_type_): _description_
    """
    polygon = param.Dict(default={'coordinates': [[[-110.390625, 39.878267],
                                                   [-88.242187, 40.682859],
                                                   [-85.078125, -7.403143],
                                                   [-119.179688, 2.06791],
                                                   [-110.390625, 39.878267]]]})
