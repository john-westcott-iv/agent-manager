# Initial release:
Test the code output (ensure it works with AI agent)
Create LICENSE.md file
Push the code somewhere?

# Feature ideas
Cache md5 sums of the files in the different repos so we can quickly know if we need to merge on a subsequent run.

# Create process
Create a background process that would somehow detect changes and auto-update repos for users.

# Alternative Markdown Merge Strategy
Instead of just appending one after another can we merge sections based on heading in the markdown?
i.e. if one file had the section: # Top Level > ## Indented One
     and a subsequent file had: # Top Level > ## Indent One

    We currently output:
    # Top Level
    ## Indent One
    Content A
    <!-- Notification that the following has higher priority -->
    # Top Level
    ## Indent One
    Content B
    
    Instead could we do:
    # Top Level
    ## Indent One
    Content A
    <!-- notification -->
    Content B

