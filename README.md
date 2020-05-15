# git-rbr: "recursive rebase"

**NOTE**: This repository is no longer maintained and may not be up-to-date.

## Running tests

[![Build Status](https://travis-ci.org/dropbox/git-rbr.svg?branch=master)](https://travis-ci.org/dropbox/git-rbr)

From the root of the repo, run

    $ py.test

Dependencies for the test suite:

* **pytest**: `pip install pytest`

* **Git v2.7 or later**: if your Git version is too old, install a
  current one from https://git-scm.com/downloads or
  https://launchpad.net/~git-core/+archive/ubuntu/ppa .
  (`git-rbr` itself should work with much older versions of Git...
  though we don't currently test that automatically.)

## License

Copyright 2017 Dropbox, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
