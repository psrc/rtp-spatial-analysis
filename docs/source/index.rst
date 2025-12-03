.. RTP Spatial Analysis documentation master file, created by
   sphinx-quickstart on Wed Dec  3 11:52:41 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

RTP Spatial Analysis documentation
==================================

Add your content using ``reStructuredText`` syntax. See the
`reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
documentation for details.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

This project contains several scripts that overlay and summarize projects
for the 2026 RTP. 

Density and Freight  
-------------------

The Density and Freight analysis can be run by setting `run_density_and_freight` to `True`.
See ./rtp_spatial_analysis/configs/config.yaml for this setting. 

Then run the script as so, from the root directory of this repo::

   python .\rtp_spatial_analysis\src\run.py -c rtp_spatial_analysis\configs 

Some other subheading
---------------------

And here is some more documentation placeholder text

