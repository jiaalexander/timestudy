
Database Enhancement
* Record the CNAME of every query in the times database.
  getipbyhostname_ex
* Transparent databsae upgrades? We probably don't have enough out there yet. 

Reporing Enhancement:
* So one suggestion was if number of IPs is > N, we join series by CNAME.  From what I can see that will collapse all couldfront lists to one CNAME.

Sampling and Recording Enahncement:
* One per day, unless CONDITION is met.
* CONDITION = an errornous time within the past 7 days
* If CONDITION is met, record all samples (good and bad)

Real time reports:
Proposal is for a CGI script that displays a form if called without arguments, otherwise just performs the search.




Specify:
* Start time
* End time
* group by = hour, day, month

For each line, reports:
* start and end times
* # of queries
* # that were wrong, and %
* average offset
* stddev
* Regression of the points. We can calculate y=mx+b with a simple linear regression, but I want to report x=-b/m, which is the value of x when Y is 0. For the hosts that drift, this would be the time of the reboot, which is kind of neat.

Separately: I want to add the 0s to the graph, in a different color.

Bring back the hostname graph (as opposed to the IP address).  Have all IP addresses in slightly different colors.

I’m going to be refactoring the drawing program so that it’s a callable function in which I can specify all of those parameters. I think that I can get the drawing time down to less than a second for an IP address.

Sound good?