# Reserved Attribute Names in Jobs

When recalling the experience of learning different programming languages, I remember [Java](https://en.wikipedia.org/wiki/Java_(programming_language)) being pretty difficult and boring while liking [Python](https://en.wikipedia.org/wiki/Python_(programming_language)) very much. Many people shared similar experiences when it comes to the two languages. 

While there might be different reasons, I know for me, what made Python different from other languages is the ability to "do stuff" much quicker. The `hello world` experience was one or two lines of code, and getting to do useful things like getting `show version` output from switches was not far beyond that, thanks to the vast number of existing libraries. 

However, at some point, I had to come back to learn more about the "boring stuff" in order to progress further. Topics such as object-oriented programming, dynamic type-checking, garbage collection, and other topics are not exactly fun, but by then I was already hooked. Learning the boring topics was not so bad when I already realized the power the tool can give me.

Hopefully we have done enough to give you a taste of the power and fun aspect of Nautobot Jobs in the last 28 days of challenges. Today's challenge will be a little dull but necessary. 

We will begin by learning more about the [Reserved Attribute Names](https://docs.nautobot.com/projects/core/en/stable/development/jobs/#reserved-attribute-names) in Nautobot Job class. 


## Environment Setup

For today's challenge we do not need the Codepsace lab unless you want to launch it and compare it with the reading. If that is the case, feel free to consult [Lab Setup Scenario 1](../Lab_Setup/scenario_1_setup/README.md) to launch the lab. 

## Reserved Attribute Names

There are many attributes and methods of the Job class that serve as reserved names. This is similar to the [Python keywords](https://realpython.com/python-keywords/) that we should not use. For example, imagine how confusing it would be if you use `for` or `def` as variable or function names. 

There are [special method names](https://docs.nautobot.com/projects/core/en/stable/development/jobs/#special-methods) that we should not use: 

- `before_start()`
- `run()`
- `on_success()`
- `on_failure()`
- `after_return()`

There are other [metadata attributes](https://docs.nautobot.com/projects/core/en/stable/development/jobs/#special-methods) that we should be aware of: 

- name
- description
- approval_required
- dryrun_default
- field_order
- has_sensitive_variables
- hidden
- is_singleton
- read_only
- soft_time_limit
- task_queues
- template_name
- time_limit

As time goes on, there might be subtraction or additions to the list. There is no need to memorize them, rather just a good idea to be aware of them and bookmark the page as a reference. 

Today is a pretty short challenge, please use the rest of the time to glance through [Jobs Developer Guide](https://docs.nautobot.com/projects/core/en/stable/development/jobs/) if you have not done so already. 

## Day 29 To Do

Remember to stop the codespace instance on [https://github.com/codespaces/](https://github.com/codespaces/). 

Please post something you learned from reading the [Jobs Developer Guide](https://docs.nautobot.com/projects/core/en/stable/development/jobs/) on a social media of your choice, make sure you use the tag `#100DaysOfNautobot` `#JobsToBeDone` and tag `@networktocode`, so we can share your progress! 

In tomorrow's challenge, we will learn about using Nautobot Secret Groups for Nautobot Jobs. See you tomorrow! 

[X/Twitter](<https://twitter.com/intent/tweet?url=https://github.com/nautobot/100-days-of-nautobot&text=I+just+completed+Day+29+of+the+100+days+of+nautobot+!&hashtags=100DaysOfNautobot,JobsToBeDone>)

[LinkedIn](https://www.linkedin.com/) (Copy & Paste: I just completed Day 29 of 100 Days of Nautobot, https://github.com/nautobot/100-days-of-nautobot, challenge! @networktocode #JobsToBeDone #100DaysOfNautobot) 
