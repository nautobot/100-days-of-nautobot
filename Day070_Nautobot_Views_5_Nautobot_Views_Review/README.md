# Nautobot Views Review

Over Days 66 to 69, we delved into the intricacies of Nautobot views, focusing primarily on class-based views (CBVs), `NautbotUIVewSet`, Nautobot Generic Views, and `mixins`. It is obvious that we've only scratched the surface of these respected topics. 

In today's challenge, we will do a consolidated review of the last few days.

## Key Concepts

1. Django Class-Based Views (CBVs): CBVs provide a structured way to manage views, emphasizing code reusability and the ability to leverage existing methods.
    - **Key CBVs**:
        - TemplateView: Renders a template.
        - ListView: Displays a list of objects.
        - DetailView: Shows detail of a single object.
        - CreateView/UpdateView/DeleteView: Manage object lifecycle.

2. Nautobot Generic Views: Nautobot extends Django CBVs to suit its specific needs.
    - **Common Nautobot Generic Views**:
        - ObjectView/ObjectListView: For detail and list views of objects.
        - ObjectEditView/ObjectDeleteView: For editing and deleting operations.
        - Bulk Operations: Handling multiple objects at once with BulkEditView and BulkDeleteView.

3. NautobotUIViewSet: Viewsets organize related views in a cohesive manner.
    - **Common NautobotUIViewSet**:
        - DetailViewSet: Displays detailed info about a single object.
        - ListViewSet: Handles lists of objects.
        - EditViewSet: For creating and editing objects.
        - DestroyViewSet: Manages object deletion.
        - BulkUpdateViewSet/BulkDestroyViewSet: Enable batch operations for efficiencies.

Models and views are two foundational topics for Nautobot apps. *For the rest of the time in today's challenge, please pick a topic (or all of them) from the resources sections that interests you and read more about it.* 

## Resources
- [Best Practices](https://docs.nautobot.com/projects/core/en/stable/development/core/best-practices/)
- [Generic Views](https://docs.nautobot.com/projects/core/en/stable/development/core/generic-views/)
- [NautobotUIViewSet](https://docs.nautobot.com/projects/core/en/stable/development/apps/api/views/nautobotuiviewset/)
- [Nautobot Apps Views Code Reference](https://docs.nautobot.com/projects/core/en/stable/code-reference/nautobot/apps/views/#nautobot.apps.views.BulkCreateView)


## Day 70 To Do

Remember to stop the codespace instance on [https://github.com/codespaces/](https://github.com/codespaces/). 

Go ahead and post your understanding from today's challenge on different views in Nautobot apps, make sure you use the tag `#100DaysOfNautobot` `#JobsToBeDone` and tag `@networktocode`, so we can share your progress! 

In tomorrow's challenge, we will discuss UI styling with CSS. See you tomorrow! 

[X/Twitter](<https://twitter.com/intent/tweet?url=https://github.com/nautobot/100-days-of-nautobot&text=I+just+completed+Day+70+of+the+100+days+of+nautobot+challenge+!&hashtags=100DaysOfNautobot,JobsToBeDone>)

[LinkedIn](https://www.linkedin.com/) (Copy & Paste: I just completed Day 70 of 100 Days of Nautobot, https://github.com/nautobot/100-days-of-nautobot-challenge, challenge! @networktocode #JobsToBeDone #100DaysOfNautobot) 