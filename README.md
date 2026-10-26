# Implitag

Implitag is a complex tagging system with a simple image board built on it for
demonstrative purposes. It comprehensively solves an issue with simplistic
tagging systems.

# Features

- Item index - full view of all non-delisted items
- Item tagging
- Item search - search by tags
- Item delisting - remove an item from search results and the index
- Reverse polish notation for complex searches\*
- Tag editing - edit the details of a tag (name, description, implies, implied
by (see below))
- Tag index
- Random item link
- Pagination
- Search autocomplete

\*see below for elaboration

## Tagging system

In a simplistic tagging system (that is, one where there are items, there are
tags, and each item either does or does not have any specific tag), there is a
glaring problem of redundancy.

For example, say you're tagging images. You may have the tags "plant", "tree",
and "oak tree". A picture of an oak tree qualifies as all of these, so it
follows that it should have all 3 tags. However, that is redundant. All oak
trees are trees and all trees are plants, therefore, it would make no sense to
have the tag "tree" without the tag "plant" or have the tag "oak tree" without
both "tree" and "plant". In other words, "plant" is *implied* by "tree" which,
in turn, is *implied* by "oak tree".

The separate tagging of "tree" and "plant" on an image with the tag "oak tree"
is redundant. However, in a simplistic tagging system, they cannot reasonably
be omitted as people looking for trees would want an image with just the tag
"oak tree". It also creates the burden of ensuring that such redundant tags
have not been forgotten by whoever did the tagging.

The system implemented here functions on one additional principle which
completely solves the detailed issues. A tag may imply another. In our example,
"oak tree" would imply "tree" which would then imply "plant". By saying that
some tag "A" implies some other tag "B", you are telling the system that items
tagged with "A" should be considered a proper subset of items tagged with "B".

Specifically, a tag cannot imply itself and implication is transitive. This in
turn means (logically) that one cannot have a loop. If "A" implies "B", and
"B" implies "C", then it follows that "C" cannot imply "A". Strictly, if tags
are considered vertices in a directed graph where an edge from "A" to "B"
indicates that "A" implies "B", said graph must be strictly unidirectional and
acyclic.

When a search is made on this system, the items resulting from any given tag
are not just the items with that tag but the items with any tag which implies
it, directly or indirectly. Returning to the above example, a search for
"plant" is implicitly a search for items with "plant", "tree", "oak tree", or
any other tags which imply "plant" somehow.

This system removes the need for the redundant tags as they are implied. It
makes it impossible to accidentally omit said implied tags as they needn't be
added manually in the first place. It reduces the work of tagging items as the
most specific applicable tags can be chosen, implying many less specific tags.

## Search system

The search implements [Reverse Polish
Notation](https://en.wikipedia.org/wiki/Reverse_Polish_notation) allowing the
user to combine tags with AND, OR, NOT, and XOR operations and create
arbitrarily complex search queries without the need for parentheses.

The search takes each tag in the search expression and expands it to the full
set of tags which imply it, including itself. Then, it queries the database for
all items tagged with each of the tags in the expanded set, logically ORing
them together to get a full set of items which explicitly or implicitly are
tagged with the original tag in the search query. Then, the RPN operators are
applied to the resulting sets. If there is more than one set left after
evaluation, they are ANDed together. This specific detail means that users
needn't explicitly include AND operators in a basic search query for multiple
tags; they are implicitly ANDed together. Finally, the resulting items are
collected in a results page and presented to the user.

## Tech stack

- tagging system - Python, SQLite
- backend - Python, Flask
- frontend - HTML, CSS, JS
- configuration - JSON
