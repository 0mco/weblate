Administration
==============

Administration of Weblate is done through standard Django admin interface,
which is available under :file:`/admin/` URL.

Adding new resources
--------------------

All translation resources need to be available as Git repositories and are
organized as project/subproject structure.

Weblate supports wide range of translation formats supported by translate
toolkit, for example:

* GNU Gettext
* XLIFF
* Java properties
* Windows RC files
* Qt Linguist .ts
* Symbian localization files
* CSV
* INI

.. seealso:: http://translate.sourceforge.net/wiki/toolkit/formats

.. _project:

Project
-------

To add new resource to translate, you need to create translation project first.
The project is sort of shelf, in which real translations are folded. All
subprojects in same project share suggestions and dictionary, also the
translations are automatically propagated through the all subproject in single
project.

The project has only few attributes giving translators information about
project.

.. _subproject:

Subproject
----------

Subproject is real resource for translating. You enter Git repository location
and file mask which files to translate and Weblate automatically fetches the Git
and finds all translated files.

Should the language definition for translation be missing, empty definition is
created and named as "cs_CZ (generated)". You should adjust the definition and
report this back to Weblate authors so that missing language can be included in
next release.

The subproject contains all important parameters for working with Git and
getting translations out of it:

Repo
    Git repository used to pull changes.

    This can be either real Git URL or ``weblate://project/subproject``
    indicating that Git repository should be shared with another subproject.
Push
    Git URL used for pushing, this is completely optional and push support will
    be disabled when this is empty.
Repoweb
    URL of repository browser to display source files (location where messages
    are used). When empty no such links will be generated.

    For example on GitHub, you would use something like ``https://github.com/nijel/weblate-hello/blob/%(branch)s/%(file)s#L%(line)s``. 
Branch
    Which brach to checkout from the Git and where to look for translations.
Filemask
    Mask of files to translate including path. It should include one *
    replacing language code. In case your Git repository contains more than one
    translation files (eg. more Gettext domains), you need to create separate
    subproject for each. For example ``po/*.po`` or
    ``locale/*/LC_MESSAGES/django.po``.

.. note::
   
    As setup of translation project includes fetching Git repositories, you
    might want to preseed these, repos are stored in path defined by
    :envvar:`GIT_ROOT` in :file:`settings.py` in :file:`<project>/<subproject>`
    directories.

.. _autocreate:

Automatic creation of subprojects
---------------------------------

In case you have project with dozen of po files, you might want to import all
at once. This can be achieved using :command:`manage.py import_project`.

First you need to create project which will contain all subprojects and then
it's just a matter of running :command:`manage.py import_project`.

.. seealso:: :ref:`manage`

Updating repositories
---------------------

You should set up some way how backend repositories are updated from their
source. You can either use hooks (see :ref:`hooks`) or just regularly run
:command:`./manage.py updategit --all`.

With Gettext po files, you might be often bitten by conflict in PO file
headers. To avoid it, you can use shipped merge driver
(:file:`examples/git-merge-gettext-po`). To use it just put following
configuration to your :file:`.gitconfig`:

.. code-block:: ini

   [merge "merge-gettext-po"]
     name = merge driver for gettext po files
     driver = /path/to/weblate/examples/git-merge-gettext-po %O %A %B

And enable it's use by defining proper attributes in given repository (eg. in
:file:`.git/info/attribute`)::

    *.po merge=merge-gettext-po

.. note::

    This merge driver assumes the changes in POT files always are done in brach
    we're trying to merge.

.. seealso:: http://www.no-ack.org/2010/12/writing-git-merge-driver-for-po-files.html

Pushing changes
---------------

Each project can have configured push URL and in such case Weblate offers
button to push changes to remote repo in web interface.

I case you will use SSH for pushing, you need to have key without passphrase
(or use ssh-agent for Django) and the remote server needs to be verified by you
first, otherwise push will fail.

Interacting with others
-----------------------

Weblate makes it easy to interact with others using it's API.

.. seealso:: :ref:`api`

.. _privileges:

Access control
--------------

Weblate uses privileges system based on Django. It defines following extra privileges:

* Can upload translation [Users, Managers]
* Can overwrite with translation upload [Users, Managers]
* Can define author of translation upload  [Managers]
* Can force commiting of translation [Managers]
* Can update translation from git [Managers]
* Can push translations to remote git [Managers]
* Can do automatic translation using other project strings [Managers]
* Can lock whole translation project [Managers]
* Can reset translations to match remote git [Managers]
* Can save translation [Users, Managers]
* Can accept suggestion [Users, Managers]
* Can accept suggestion [Users, Managers]
* Can import dictionary [Users, Managers]
* Can add dictionary [Users, Managers]
* Can change dictionary [Users, Managers]
* Can delete dictionary [Users, Managers]

The default setup (after you run :program:`./manage.py setupgroups`) consists
of two groups `Users` and `Managers` which have privileges as descibed above.
All new users are automatically added to `Users` group.

To customize this setup, it is recommended to remove privileges from `Users`
group and create additional groups with finer privileges (eg. `Translators`
group, which will be allowed to save translations and manage suggestions) and
add selected users to this group. You can do all this from Django admin
interface.

.. _lazy-commit:

Lazy commits
------------

Default behaviour (configured by :envvar:`LAZY_COMMITS`) of Weblate is to group
commits from same author into one if possible. This heavily reduces number of
commits, however you might need to explicitely tell to do the commits in case
you want to get Git repository in sync, eg. for merge (this is by default
allowed for Managers group, see :ref:`privileges`).

The changes are in this mode committed once any of following conditions is
fulfilled:

* somebody else works on the translation
* merge from upstream occurs
* import of translation happens
* translation for a language is completed
* explicit commit is requested

.. _custom-checks:

Customizing checks
------------------

Weblate comes with wide range of consistency checks (see :ref:`checks`), though
they might not 100% cover all you want to check. The list of performed checks
can be adjusted using :envvar:`CHECK_LIST` and you can also add custom checks.
All you need to do is to subclass :class:`trans.checks.Check`, set few
attributes and implement either ``check`` or ``check_single`` methods (first
one if you want to deal with plurals in your code, the latter one does this for
you). You will find below some examples.

Checking translation text does not contain "foo"
++++++++++++++++++++++++++++++++++++++++++++++++

This is pretty simple check which just checks whether translation does not
contain string "foo".

.. code-block:: python

    from weblate.trans.checks import Check
    from django.utils.translation import ugettext_lazy as _

    class FooCheck(Check):

        # Used as identifier for check, should be unique
        check_id = 'foo'

        # Short name used to display failing check
        name = _('Foo check')

        # Description for failing check
        description = _('Your translation is foo')

        # Real check code
        def check_single(self, source, target, flags, language, unit):
            return 'foo' in target

Checking Czech translation text plurals differ
++++++++++++++++++++++++++++++++++++++++++++++

Check using language information to verify that two plural forms in Czech
language are not same.

.. code-block:: python

    from weblate.trans.checks import Check
    from django.utils.translation import ugettext_lazy as _

    class PluralCzechCheck(Check):

        # Used as identifier for check, should be unique
        check_id = 'foo'

        # Short name used to display failing check
        name = _('Foo check')

        # Description for failing check
        description = _('Your translation is foo')

        # Real check code
        def check(self, sources, targets, flags, language, unit):
            if self.is_language(language, ['cs']):
                return targets[1] == targets[2]
            return False
