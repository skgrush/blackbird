# Blackbird
> A python module for accessing Blackboard.

[![Python Version][pyver-image]]()
[![Project Status][status-image]]()
[![License][license-image]][license-url]

I originally started Blackbird in mid-2013 and continued development through 
late 2014 when I finally realized what a **ridiculous monstrosity Blackboard
is**, halting development to retain my sanity. Essentially, the module can
be used, but it is *far* from complete. _Blackbird has **never** been tested
on any Blackboard installation outside of Missouri S&T._

This repo contains various support scripts that were never fully implemented
into Blackbird itself, including [`manifest_module.py`](manifest_module.py)
which was planned to be a binary manifest file implementation but was
abandoned, and the [`bb_tk`](bb_tk) submodule which provides a graphical 
frontend for certain aspects of Blackbird (in partial working order).

## Example
*Requires valid Missouri S&T credentials by default.*
```python
import blackbird
bb = blackbird.Blackboard()
bb.login()
...
bb.update_courses()
mycourse = bb.courses[1]
bb.update_course_content(mycourse)

import bb_tk
import bb_tk.tree_browser as tree_browser
tb = tree_browser.content_tree(None)
tb.set_course(mycourse)
tb.generate()
```

[pyver-image]: https://img.shields.io/badge/python-v2.7-blue.svg
[status-image]: https://img.shields.io/badge/status-dead-red.svg
[license-image]: https://img.shields.io/github/license/skgrush/blackbird.svg
[license-url]: ./LICENSE.md
