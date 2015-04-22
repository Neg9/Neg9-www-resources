# Neg9-www-resources

This repository holds somewhat dynamic resources that are hosted on, and used on the Neg9.org website. Examples of such data include presentations and papers created by Neg9 members, resources from meetings or projects, and graphics (such as screenshots) for news postings, write-ups, etc.

All content it publicly available from https://neg9.org/resources/ or directly from this Git repository. The content on Neg9.org is a clone of this repository.

## Organizational standards:

* Filenames MUST NOT contain whitespace.
* **/presentations**: Hosted presentations from Neg9 members, possibly talks at Neg9 meetings or conferences, etc.
  * Filenames SHOULD be in the format of ``[ISO-8601-Date]_[ContentCreator-With-Hyphens]_[Content-Title-With-Hyphens].[extension]``, e.g.:
    * ``2015-04-15_Neg9-tecknicaltom-meta_CTF-Toolkit.pdf``
* **/media**: Screenshots or other graphics, audio files, etc. that may be used in news postings for CTF writeups, etc.
  * Files should be placed in a directory in the name of the news item SLUG, if appropriate.
  * File paths SHOULD be in the format of ``[NewsItem-SLUG]/[File-Description].[extension]``, e.g.:
    * ``plaidctf-2015-eces-revenge2-misc-250-writeup/ModelSim-01.png``
