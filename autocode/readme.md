## autocode
An automatic coder to generate codes with a source code format and detail definitions. The tool is especially useful if your database columns keep changing but some basic functions like insert/remove/update/... remain basically the same except for some minor changes related to some columns.
With autocode, you can simply define database access code formats and database columns, and let the computer do the repeated work.

The funtions were designed for mysql access in golang, but you can create your own version for various tasks.
An example is given.
The example parses data.txt and table.txt according to definitions in exp_defines.txt.
exp_templates.txt shows template names and target names.