import os
import tifffile


def is_brainreg_dir(path):
    """Determines whether a path is to a brainreg output directory

    Parameters
    ----------
    path : str
        Path to file.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    path = os.path.abspath(path)
    if os.path.isdir(path):
        filelist = os.listdir(path)
    else:
        return False
    if "brainreg.json" in filelist:
        return True
    return False


def load_additional_downsampled_channels(
    path,
    layers,
    extension=".tiff",
    search_string="downsampled_",
    exlusion_string="downsampled_standard",
):

    # Get additional downsampled channels, but not main one, and not those
    # in standard space

    for file in path.iterdir():
        if (
            (file.suffix == extension)
            and file.name.startswith(search_string)
            and not file.name.startswith(exlusion_string)
        ):

            print(
                f"Found additional downsampled image: {file.name}, "
                f"adding to viewer"
            )
            name = file.name.strip(search_string).strip(extension) + (
                " (downsampled)"
            )
            layers.append(
                (
                    tifffile.imread(file),
                    {"name": name, "visible": False},
                    "image",
                )
            )

    return layers
