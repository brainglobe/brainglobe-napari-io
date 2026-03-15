# napari-brainglobe-io

[![License](https://img.shields.io/pypi/l/brainglobe-napari-io.svg?color=green)](https://github.com/brainglobe/brainglobe-napari-io/blob/main/LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/brainglobe-napari-io.svg?color=green)](https://python.org)
[![PyPI](https://img.shields.io/pypi/v/brainglobe-napari-io.svg?color=green)](https://pypi.org/project/brainglobe-napari-io)
[![Anaconda version](https://anaconda.org/conda-forge/brainglobe-napari-io/badges/version.svg)](https://anaconda.org/conda-forge/brainglobe-napari-io)
[![Napari hub](https://img.shields.io/endpoint?url=https://npe2api-git-add-shields-napari.vercel.app/api/shields/brainglobe-napari-io)](https://napari-hub.org/plugins/brainglobe-napari-io.html)
[![PyPI Downloads](https://pepy.tech/badge/brainglobe-napari-io)](https://pepy.tech/project/brainglobe-napari-io)
[![tests](https://github.com/brainglobe/brainglobe-napari-io/workflows/tests/badge.svg)](https://github.com/brainglobe/brainglobe-napari-io/actions)
[![codecov](https://codecov.io/gh/brainglobe/brainglobe-napari-io/branch/main/graph/badge.svg)](https://codecov.io/gh/brainglobe/brainglobe-napari-io)
[![image.sc forum](https://img.shields.io/badge/dynamic/json.svg?label=forum&url=https%3A%2F%2Fforum.image.sc%2Ftags%2Fbrainglobe.json&query=%24.topic_list.tags.0.topic_count&colorB=brightgreen&suffix=%20topics&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAABPklEQVR42m3SyyqFURTA8Y2BER0TDyExZ+aSPIKUlPIITFzKeQWXwhBlQrmFgUzMMFLKZeguBu5y+//17dP3nc5vuPdee6299gohUYYaDGOyyACq4JmQVoFujOMR77hNfOAGM+hBOQqB9TjHD36xhAa04RCuuXeKOvwHVWIKL9jCK2bRiV284QgL8MwEjAneeo9VNOEaBhzALGtoRy02cIcWhE34jj5YxgW+E5Z4iTPkMYpPLCNY3hdOYEfNbKYdmNngZ1jyEzw7h7AIb3fRTQ95OAZ6yQpGYHMMtOTgouktYwxuXsHgWLLl+4x++Kx1FJrjLTagA77bTPvYgw1rRqY56e+w7GNYsqX6JfPwi7aR+Y5SA+BXtKIRfkfJAYgj14tpOF6+I46c4/cAM3UhM3JxyKsxiOIhH0IO6SH/A1Kb1WBeUjbkAAAAAElFTkSuQmCC)](https://forum.image.sc/tag/brainglobe)
[![Bluesky](https://img.shields.io/badge/Bluesky-0285FF?logo=bluesky&logoColor=fff)](https://bsky.app/profile/brainglobe.info)
[![Mastodon](https://img.shields.io/badge/Mastodon-6364FF?logo=mastodon&logoColor=fff)](https://mastodon.online/@brainglobe)

Visualise cellfinder and brainreg results with napari


----------------------------------


## Installation
This package is likely already installed
(e.g. with cellfinder, brainreg or another napari plugin), but if you want to
install it again, either use the napari plugin install GUI or you can
install `brainglobe-napari-io` via [pip]:

    pip install brainglobe-napari-io

## Usage
* Open napari (however you normally do it, but typically just type `napari` into your terminal, or click on your desktop icon)

### brainreg
#### Sample space
Drag your [brainreg](https://github.com/brainglobe/brainreg) output directory (the one with the log file) onto the napari window.

Various images should then open, including:
* `Registered image` - the image used for registration, downsampled to atlas resolution
* `atlas_name` - e.g. `allen_mouse_25um` the atlas labels, warped to your sample brain
* `Boundaries` - the boundaries of the atlas regions

If you downsampled additional channels, these will also be loaded.

Most of these images will not be visible by default. Click the little eye icon to toggle visibility.

_N.B. If you use a high resolution atlas (such as `allen_mouse_10um`), then the files can take a little while to load._

![sample_space](https://raw.githubusercontent.com/brainglobe/brainglobe-napari-io/master/resources/sample_space.gif)


#### Atlas space
`napari-brainreg` also comes with an additional plugin, for visualising your data
in atlas space.

This is typically only used in other software, but you can enable it yourself:
* Open napari
* Navigate to `Plugins` -> `Plugin Call Order`
* In the `Plugin Sorter` window, select `napari_get_reader` from the `select hook...` dropdown box
* Drag `brainreg_read_dir_atlas_space` (the atlas space viewer plugin) above `brainreg_read_dir` (the normal plugin) to ensure that the atlas space plugin is used preferentially.


### cellfinder
#### Load cellfinder XML/YAML file
* Load your raw data (drag and drop the data directories into napari, one at a time)
* Drag and drop your cellfinder XML/YAML file (e.g. `cell_classification.xml`) into napari.

#### Load cellfinder directory
* Load your raw data (drag and drop the data directories into napari, one at a time)
* Drag and drop your cellfinder output directory into napari.

The plugin will then load your detected cells (in yellow) and the rejected cell
candidates (in blue). If you carried out registration, then these results will be
overlaid (similarly to the loading brainreg data, but transformed to the
coordinate space of your raw data).

![load_data](https://raw.githubusercontent.com/brainglobe/brainglobe-napari-io/master/resources/load_data.gif)
**Loading raw data**

![load_data](https://raw.githubusercontent.com/brainglobe/brainglobe-napari-io/master/resources/load_results.gif)
**Loading cellfinder results**

## Seeking help or contributing
We are always happy to help users of our tools, and welcome any contributions. If you would like to get in contact with us for any reason, please see the [contact page of our website](https://brainglobe.info/contact.html).
