A curses git committing utility
===============================

- Split panel, one panel display the status of your work tree, what is going to be committed etc..
- The other panel displays the diff of the selected file
- Coloured diff
- Syntax highlight (uses highlight binary)

Key bindings
============
- `Up`, `down` : Select previous/next file
- `j`, `k`: Scroll diff view down/up
- `Home` / `End` or `g` / `G`: Go to beginning / end of diff view
- `J` / `K` or `npage` `ppage`: Scroll one page down / up in the diff view
- `a`: Add the selected file to the index (`git add <file>`)
- `r`: Reset the file (`git reset HEAD <file>`)
- `c`: Checkout the file (`git checkout <file>`) (CHANGES WILL BE LOST!)
- `e`: Edit file
- Enter: Commit (`git commit`)
- `q`: Quit

File Status
===========
Gitco shows the file's status in git's short-format status. From git docs:

In the short-format, the status of each path is shown as

`XY PATH1 -> PATH2`

where PATH1 is the path in the HEAD, and the " -> PATH2" part is shown only when PATH1 corresponds to a different path in the index/worktree (i.e. the file is renamed). The XY is a two-letter status
code.

For paths with merge conflicts, X and Y show the modification states of each side of the merge. For paths that do not have merge conflicts, X shows the status of the index, and Y shows the status of
the work tree. For untracked paths, XY are ??. Other status codes can be interpreted as follows:

- ` ` = unmodified
- `M` = modified
- `A` = added
- `D` = deleted
- `R` = renamed
- `C` = copied
- `U` = updated but unmerged

Ignored files are not listed

```
X          Y     Meaning
-------------------------------------------------
          [MD]   not updated
M        [ MD]   updated in index
A        [ MD]   added to index
D         [ M]   deleted from index
R        [ MD]   renamed in index
C        [ MD]   copied in index
[MARC]           index and work tree matches
[ MARC]     M    work tree changed since index
[ MARC]     D    deleted in work tree
-------------------------------------------------
D           D    unmerged, both deleted
A           U    unmerged, added by us
U           D    unmerged, deleted by them
U           A    unmerged, added by them
D           U    unmerged, deleted by us
A           A    unmerged, both added
U           U    unmerged, both modified
-------------------------------------------------
?           ?    untracked
!           !    ignored
-------------------------------------------------
```

Screen shoot
============

![gitco screenshoot](http://i.imgur.com/cmcnRVK.png)

