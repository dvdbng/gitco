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

Screen shoot
============

![gitco screenshoot](http://i.imgur.com/cmcnRVK.png)

