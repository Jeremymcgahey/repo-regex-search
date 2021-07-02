# repo-regex-search
A tool to search a users repositories using a regex string.<br />
There are environment variables that need to be set: GIT_ACCESS_TOKEN and GIT_USERNAME. <br />
The output is a json dump of the repository api links. <br />
The default implementation searches .docker/build/Dockerfile for version issues <br />
The command line parameters are -r, -v, -p, -s, -gc, -b. -h will provide a help menu with further explanation. <br />
A good command example would be python repo-scan.py -s ”FROM node\:[0-9\.]+” > C:\Users\Work\Desktop\output.txt | type C:\Users\Work\Desktop\output.txt <br />
This will output the repository links that aren't in FROM node:10. etc.. into a text file.  


