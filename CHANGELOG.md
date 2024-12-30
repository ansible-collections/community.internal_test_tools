# Community Internal Test Tools Collection Release Notes

**Topics**

- <a href="#v0-13-0">v0\.13\.0</a>
    - <a href="#release-summary">Release Summary</a>
    - <a href="#minor-changes">Minor Changes</a>
- <a href="#v0-12-0">v0\.12\.0</a>
    - <a href="#release-summary-1">Release Summary</a>
    - <a href="#minor-changes-1">Minor Changes</a>
    - <a href="#removed-features-previously-deprecated">Removed Features \(previously deprecated\)</a>
- <a href="#v0-11-0">v0\.11\.0</a>
    - <a href="#release-summary-2">Release Summary</a>
    - <a href="#minor-changes-2">Minor Changes</a>
    - <a href="#breaking-changes--porting-guide">Breaking Changes / Porting Guide</a>
    - <a href="#deprecated-features">Deprecated Features</a>
    - <a href="#bugfixes">Bugfixes</a>
- <a href="#v0-10-1">v0\.10\.1</a>
    - <a href="#release-summary-3">Release Summary</a>
- <a href="#v0-10-0">v0\.10\.0</a>
    - <a href="#release-summary-4">Release Summary</a>
    - <a href="#removed-features-previously-deprecated-1">Removed Features \(previously deprecated\)</a>
    - <a href="#known-issues">Known Issues</a>
- <a href="#v0-9-0">v0\.9\.0</a>
    - <a href="#release-summary-5">Release Summary</a>
    - <a href="#minor-changes-3">Minor Changes</a>
    - <a href="#deprecated-features-1">Deprecated Features</a>
- <a href="#v0-8-0">v0\.8\.0</a>
    - <a href="#release-summary-6">Release Summary</a>
    - <a href="#minor-changes-4">Minor Changes</a>
- <a href="#v0-7-0">v0\.7\.0</a>
    - <a href="#release-summary-7">Release Summary</a>
    - <a href="#minor-changes-5">Minor Changes</a>
- <a href="#v0-6-1">v0\.6\.1</a>
    - <a href="#release-summary-8">Release Summary</a>
    - <a href="#bugfixes-1">Bugfixes</a>
- <a href="#v0-6-0">v0\.6\.0</a>
    - <a href="#release-summary-9">Release Summary</a>
    - <a href="#minor-changes-6">Minor Changes</a>
    - <a href="#bugfixes-2">Bugfixes</a>
- <a href="#v0-5-0">v0\.5\.0</a>
    - <a href="#release-summary-10">Release Summary</a>
    - <a href="#minor-changes-7">Minor Changes</a>
    - <a href="#breaking-changes--porting-guide-1">Breaking Changes / Porting Guide</a>
    - <a href="#bugfixes-3">Bugfixes</a>
- <a href="#v0-4-0">v0\.4\.0</a>
    - <a href="#release-summary-11">Release Summary</a>
    - <a href="#minor-changes-8">Minor Changes</a>
    - <a href="#bugfixes-4">Bugfixes</a>
- <a href="#v0-3-0">v0\.3\.0</a>
    - <a href="#minor-changes-9">Minor Changes</a>
    - <a href="#bugfixes-5">Bugfixes</a>
    - <a href="#new-plugins">New Plugins</a>
        - <a href="#lookup">Lookup</a>
    - <a href="#new-modules">New Modules</a>
- <a href="#v0-2-1">v0\.2\.1</a>
    - <a href="#release-summary-12">Release Summary</a>
- <a href="#v0-2-0">v0\.2\.0</a>
    - <a href="#major-changes">Major Changes</a>
- <a href="#v0-1-1">v0\.1\.1</a>
    - <a href="#release-summary-13">Release Summary</a>
    - <a href="#new-modules-1">New Modules</a>

<a id="v0-13-0"></a>
## v0\.13\.0

<a id="release-summary"></a>
### Release Summary

Feature release\.

<a id="minor-changes"></a>
### Minor Changes

* extra sanity tests runner \- add <code>\-\-break\-system\-packages</code> to <code>pip</code> invocations \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/137](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/137)\)\.
* extra sanity tests runner \- bump default Python version used for tests to 3\.13 \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/137](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/137)\)\.
* extra sanity tests runner \- update fallback image name and use Python 3\.13 inside the container \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/137](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/137)\)\.

<a id="v0-12-0"></a>
## v0\.12\.0

<a id="release-summary-1"></a>
### Release Summary

Feature release\.

<a id="minor-changes-1"></a>
### Minor Changes

* fetch\_url and open\_url unit test frameworks \- use the <code>tests\.unit\.compat\.mock</code> module everywhere so that <code>unittest\.mock</code> is used instead of <code>mock</code> on Python 3 \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/130](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/130)\)\.
* open\_url and fetch\_url unit test frameworks \- allow to check for form value arrays \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/125](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/125)\)\.

<a id="removed-features-previously-deprecated"></a>
### Removed Features \(previously deprecated\)

* Removed the <code>ansible\_builtin\_runtime</code> tool \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/issues/111](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/issues/111)\, [https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/131](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/131)\)\.

<a id="v0-11-0"></a>
## v0\.11\.0

<a id="release-summary-2"></a>
### Release Summary

Feature\, bugfix\, and maintenance release\.

<a id="minor-changes-2"></a>
### Minor Changes

* extra sanity test runner \- make sure that a <code>ansible\_collections</code> ancestor directory is also copied into the Docker container \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/103](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/103)\)\.

<a id="breaking-changes--porting-guide"></a>
### Breaking Changes / Porting Guide

* The internal test module <code>fetch\_url\_test\_module</code> has been renamed to <code>\_fetch\_url\_test\_module</code>\, and the internal test lookup plugin <code>open\_url\_test\_lookup</code> has been renamed to <code>\_open\_url\_test\_lookup</code>\. This emphasizes that these plugins are private and not supposed to be used by end\-users  \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/112](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/112)\)\.

<a id="deprecated-features"></a>
### Deprecated Features

* The <code>tools/ansible\_builtin\_runtime\.py</code> tool is deprecated and will be removed in a future version\. If anyone is interested in keeping this tool\, please comment on the [tool removal issue](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/issues/111) \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/issues/111](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/issues/111)\)\.

<a id="bugfixes"></a>
### Bugfixes

* extra sanity test runner \- run pip via Python instead of running it directly\; also set <code>PIP\_BREAK\_SYSTEM\_PACKAGES\=1</code> in the environment \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/104](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/104)\)\.

<a id="v0-10-1"></a>
## v0\.10\.1

<a id="release-summary-3"></a>
### Release Summary

Maintenance release to test whether publishing community collections works\.

<a id="v0-10-0"></a>
## v0\.10\.0

<a id="release-summary-4"></a>
### Release Summary

Maintenance release with updated documentation and removal of a deprecated tool\.

From this version on\, community\.internal\_test\_tools is using the new [Ansible semantic markup](https\://docs\.ansible\.com/ansible/devel/dev\_guide/developing\_modules\_documenting\.html\#semantic\-markup\-within\-module\-documentation)
in its documentation\. If you look at documentation with the ansible\-doc CLI tool
from ansible\-core before 2\.15\, please note that it does not render the markup
correctly\. You should be still able to read it in most cases\, but you need
ansible\-core 2\.15 or later to see it as it is intended\. Alternatively you can
look at [the docsite](https\://ansible\-collections\.github\.io/community\.internal\_test\_tools/branch/main/)
for the rendered HTML version of the documentation of the latest release\.

<a id="removed-features-previously-deprecated-1"></a>
### Removed Features \(previously deprecated\)

* Removed the deprecated <code>meta/runtime\.yml</code> tool \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/issues/79](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/issues/79)\, [https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/91](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/91)\)\.

<a id="known-issues"></a>
### Known Issues

* Ansible markup will show up in raw form on ansible\-doc text output for ansible\-core before 2\.15\. If you have trouble deciphering the documentation markup\, please upgrade to ansible\-core 2\.15 \(or newer\)\, or read the HTML documentation on [https\://ansible\-collections\.github\.io/community\.internal\_test\_tools/branch/main/](https\://ansible\-collections\.github\.io/community\.internal\_test\_tools/branch/main/)\.

<a id="v0-9-0"></a>
## v0\.9\.0

<a id="release-summary-5"></a>
### Release Summary

Feature release with improved extra sanity test runner\.

<a id="minor-changes-3"></a>
### Minor Changes

* Let the extra sanity test runner report bad test descriptors as errors \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/89](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/89)\)\.
* Use Python 3\.10 instead of Python 3\.8 for the extra sanity test runner \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/88](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/88)\)\.

<a id="deprecated-features-1"></a>
### Deprecated Features

* The meta/runtime\.yml helper tool <code>tools/meta\_runtime\.py</code> is deprecated and will be removed soon\. If you need it\, please comment on the issue and/or stick to a version of community\.internal\_test\_tools that is known to still includes it \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/issues/79](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/issues/79)\, [https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/90](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/90)\)\.

<a id="v0-8-0"></a>
## v0\.8\.0

<a id="release-summary-6"></a>
### Release Summary

Maintenance release with updated documentation and licensing information\.

<a id="minor-changes-4"></a>
### Minor Changes

* The collection repository conforms to the [REUSE specification](https\://reuse\.software/spec/) except for the changelog fragments \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/75](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/75)\)\.

<a id="v0-7-0"></a>
## v0\.7\.0

<a id="release-summary-7"></a>
### Release Summary

Regular feature release\.

<a id="minor-changes-5"></a>
### Minor Changes

* All software licenses are now in the <code>LICENSES/</code> directory of the collection root\. Moreover\, <code>SPDX\-License\-Identifier\:</code> is used to declare the applicable license for every file that is not automatically generated \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/69](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/69)\)\.
* open\_url and fetch\_url unit test frameworks \- allow to check for <code>timeout</code>\, <code>url\_username</code>\, <code>url\_password</code>\, and <code>force\_basic\_auth</code> settings \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/65](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/65)\)\.

<a id="v0-6-1"></a>
## v0\.6\.1

<a id="release-summary-8"></a>
### Release Summary

Regular bugfix release\.

<a id="bugfixes-1"></a>
### Bugfixes

* extra sanity test runner \- bump default Docker image fallback to container currently used by ansible\-test in devel branch \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/55](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/55)\)\.
* extra sanity test runner \- fix default Docker image detection to work with ansible\-test from ansible\-core 2\.12\.2 on \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/55](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/55)\)\.

<a id="v0-6-0"></a>
## v0\.6\.0

<a id="release-summary-9"></a>
### Release Summary

Feature and bugfix release\.

<a id="minor-changes-6"></a>
### Minor Changes

* fetch\_url test framework \- make behavior more similar to latest ansible\-core <code>devel</code> branch\, and include <code>closed</code> property for response objects \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/52](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/52)\)\.
* open\_url test framework \- include <code>closed</code> property for response objects \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/52](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/52)\)\.

<a id="bugfixes-2"></a>
### Bugfixes

* fetch\_url\_test\_module \- fix usage of <code>fetch\_url</code> with changes in latest ansible\-core <code>devel</code> branch \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/52](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/52)\)\.
* files\_collect\, files\_diff \- ignore <code>atime</code> since that does not indicate that a file was modified \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/54](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/54)\)\.

<a id="v0-5-0"></a>
## v0\.5\.0

<a id="release-summary-10"></a>
### Release Summary

Feature release with various tool improvements\.

<a id="minor-changes-7"></a>
### Minor Changes

* <code>fetch\_url</code> and <code>open\_url</code> test frameworks \- output number of expected and actual calls when number of actual calls is too low\.
* ansible\_builtin\_runtime tool \- allow to specify collection root directory for <code>check\-ansible\-core\-redirects</code> subcommand \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/51](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/51)\)\.
* ansible\_builtin\_runtime tool \- make tool executable \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/51](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/51)\)\.
* extra sanity test runner \- add options <code>\-\-bot</code> and <code>\-\-junit</code> to create results that ansibullbot and AZP can parse \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/41](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/41)\)\.
* extra sanity test runner \- bump default Python version from 3\.7 to 3\.8 \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/49](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/49)\)\.
* meta\_runtime tool \- allow to specify collection root directory for all subcommands \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/51](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/51)\)\.

<a id="breaking-changes--porting-guide-1"></a>
### Breaking Changes / Porting Guide

* ansible\_builtin\_runtime tool \- renamed <code>check\-ansible\-base\-redirects</code> subcommand to <code>check\-ansible\-core\-redirects</code> \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/51](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/51)\)\.

<a id="bugfixes-3"></a>
### Bugfixes

* ansible\_builtin\_runtime tool \- fix subcommand <code>check\-ansible\-core\-redirects</code> \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/51](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/51)\)\.
* extra sanity test runner \- bump default Docker image fallback to container currently used by ansible\-test in devel branch \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/50](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/50)\)\.
* extra sanity test runner \- fix default Docker image detection to work with ansible\-test from ansible\-core 2\.12 \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/47](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/47)\)\.

<a id="v0-4-0"></a>
## v0\.4\.0

<a id="release-summary-11"></a>
### Release Summary

Add bugfixes for and new features to the <code>open\_url</code>/<code>fetch\_url</code> test framework\.

<a id="minor-changes-8"></a>
### Minor Changes

* fetch\_url and open\_url testing frameworks \- allow to check query parameters of URLs \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/33](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/33)\)\.
* fetch\_url and open\_url testing frameworks \- allow to compare URLs without query and/or fragment \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/33](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/33)\)\.
* fetch\_url and open\_url testing frameworks \- allow to parse and check JSON data \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/34](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/34)\)\.

<a id="bugfixes-4"></a>
### Bugfixes

* fetch\_url testing framework \- return <code>url</code> as part of <code>info</code> \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/33](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/33)\)\.

<a id="v0-3-0"></a>
## v0\.3\.0

<a id="minor-changes-9"></a>
### Minor Changes

* Added a framework for testing plugins using <code>open\_url</code> from <code>ansible\.module\_utils\.urls</code> \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/24](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/24)\)\.
* The <code>fetch\_url</code> testing framework now allows to match the provided content \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/31](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/31)\)\.
* There are now a [meta/runtime\.yml and ansible\_builtin\_runtime\.yml helper tools](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/tree/main/tools/README\.md) which allows to convert between symlinks and redirects in <code>meta/runtime\.yml</code>\, allows to compare ansible\-base\'s <code>lib/ansible/config/ansible\_builtin\_runtime\.yml</code> with this collection\, and verify that plugins mentioned actually exist\.

<a id="bugfixes-5"></a>
### Bugfixes

* Fix form value present test for <code>fetch\_url</code> testing framework \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/24](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/24)\)\.
* Fix header test for <code>fetch\_url</code> testing framework \([https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/24](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/pull/24)\)\.

<a id="new-plugins"></a>
### New Plugins

<a id="lookup"></a>
#### Lookup

* community\.internal\_test\_tools\.open\_url\_test\_lookup \- Test plugin for the open\_url test framework \(DO NOT USE THIS\!\)

<a id="new-modules"></a>
### New Modules

* community\.internal\_test\_tools\.files\_collect \- Collect state of files and directories on disk
* community\.internal\_test\_tools\.files\_diff \- Check whether there were changes since files\_collect was called

<a id="v0-2-1"></a>
## v0\.2\.1

<a id="release-summary-12"></a>
### Release Summary

Re\-release because Galaxy did not accept a tag with spaces in <code>galaxy\.yml</code>\. No other changes besides that the changelog moved to the root directory\.

<a id="v0-2-0"></a>
## v0\.2\.0

<a id="major-changes"></a>
### Major Changes

* There is now a [extra sanity test runner](https\://github\.com/ansible\-collections/community\.internal\_test\_tools/tree/main/tools/README\.md) which allows to easily run extra sanity tests\. This is a stop\-gap solution until ansible\-test supports sanity test plugins\.

<a id="v0-1-1"></a>
## v0\.1\.1

<a id="release-summary-13"></a>
### Release Summary

Initial release\.

<a id="new-modules-1"></a>
### New Modules

* community\.internal\_test\_tools\.community\.internal\_test\_tools\.fetch\_url\_test\_module \- Test module for fetch\_url test framework
