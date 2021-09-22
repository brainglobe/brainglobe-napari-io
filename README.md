# napari-brainglobe-io

[![License](https://img.shields.io/pypi/l/brainglobe-napari-io.svg?color=green)](https://github.com/napari/brainglobe-napari-io/raw/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/brainglobe-napari-io.svg?color=green)](https://pypi.org/project/brainglobe-napari-io)
[![Python Version](https://img.shields.io/pypi/pyversions/brainglobe-napari-io.svg?color=green)](https://python.org)
[![tests](https://github.com/brainglobe/brainglobe-napari-io/workflows/tests/badge.svg)](https://github.com/brainglobe/brainglobe-napari-io/actions)
[![codecov](https://codecov.io/gh/brainglobe/brainglobe-napari-io/branch/master/graph/badge.svg)](https://codecov.io/gh/brainglobe/brainglobe-napari-io)

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
* Drag `brainreg_read_dir_standard_space` (the atlas space viewer plugin) above `brainreg_read_dir` (the normal plugin) to ensure that the atlas space plugin is used preferentially.


### cellfinder
#### Load cellfinder XML file
* Load your raw data (drag and drop the data directories into napari, one at a time)
* Drag and drop your cellfinder XML file (e.g. `cell_classification.xml`) into napari.

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



## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [MIT] license,
"brainglobe-napari-io" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin
[file an issue]: https://github.com/brainglobe/brainglobe-napari-io/issues
[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/



---
The BrainGlobe project is generously supported by the Sainsbury Wellcome Centre and the Institute of Neuroscience, Technical University of Munich, with funding from Wellcome, the Gatsby Charitable Foundation and the Munich Cluster for Systems Neurology - Synergy.

<img src='https://brainglobe.info/images/logos_combined.png' width="550">
