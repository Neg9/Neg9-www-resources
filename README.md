# Neg9-www-resources

## Summary
This repository holds somewhat dynamic resources that are hosted on, and used on the Neg9.org website. Examples of such data include presentations and papers created by Neg9 members, resources from meetings or projects, and graphics (such as screenshots) for news postings, write-ups, etc.

All content it publicly available from https://neg9.org/resources/ or directly from this Git repository. The content on Neg9.org is a clone of this repository.

## Detailed description

### What for?
* Presentation material from meetings, conferences, etc.
* Screenshots and other supporting files for news posts and CTF writeups on the main page of Neg9.org,
* Whatever else makes sense - semi-static content that isn't just background graphics for the site, but should persist for historical purposes and be public.
* Nothing private whatsoever - people can download the content directly from this repository on GitHub.com if they so desire.

### Why?!
* We don't want to lose stuff, and we want to host things in a consistent, organized manner.

### How!
* Git repository, hosted as a PUBLIC repo on the [Neg9 Github account](https://github.com/Neg9/Neg9-www-resources)
* It's added as a [Git Submodule](https://git-scm.herokuapp.com/book/en/v2/Git-Tools-Submodules) to the private Neg9.org website repository, which is the repo for the Neg9 website code itself.
  * This is good because we can keep the resources repo public, but easily incorporate it into the Neg9 site, even though the repo for that is private. Everything is always tracked in Git, so we don't lose things or make things inconsistent.
* This [README.md](https://github.com/Neg9/Neg9-www-resources/blob/master/README.md) file defines how files should be structured in the repository, and naming conventions so things don't get stupid. Declares there shall not be spaces in directory and file names forever, and always.
* People can easily contribute to the public resources repo when they present at a Neg9 meeting or do a writeup. This is really cool for "guest" content contributors as well.
* If people don't want to fork/commit/pull request, anyone in the Neg9 Github organization can just add stuff to it directly - not a big deal.

* The resources directory is served up directly via NGINX, without going through any Django/Python, using NGINX's optimized settings for doing what it unequivocally does best.. serve static content:

    	# Don't allow HTTP access to the submodule's .git* or README* files
    	location ~* ^/resources/(.git|README) {
    		return 404;
    	}
    
    	# More dynamic content used on news posts and such (presentations,
    screenshots, etc.)
    	location /resources/ {
    		rewrite ^/resources/(.*)$ /$1 break;
    		root /var/www/neg9.org/resources;
    		add_header Vary Accept-Encoding;
    		expires 1h;
    		sendfile on;
    		tcp_nopush on;
    		tcp_nodelay on;
    	}

## Organizational standards:

* Filenames MUST NOT contain whitespace.
* **/presentations**: Hosted presentations from Neg9 members, possibly talks at Neg9 meetings or conferences, etc.
  * Filenames SHOULD be in the format of ``[ISO-8601-Date]_[ContentCreator-With-Hyphens]_[Content-Title-With-Hyphens].[extension]``, e.g.:
    * ``2015-04-15_Neg9-tecknicaltom-meta_CTF-Toolkit.pdf``
* **/media**: Screenshots or other graphics, audio files, etc. that may be used in news postings for CTF writeups, etc.
  * Files should be placed in a directory in the name of the news item SLUG, if appropriate.
  * File paths SHOULD be in the format of ``[NewsItem-SLUG]/[File-Description].[extension]``, e.g.:
    * ``plaidctf-2015-eces-revenge2-misc-250-writeup/ModelSim-01.png``
