# Nautobot UI Component Framework

[Nautobot UI Component Framework](https://docs.nautobot.com/projects/core/en/stable/development/core/ui-component-framework/) was introduced in Nautobot v2.4 and changes how Nautobot creates object views in the application. Instead of writing HTML templates, we *declare* the UI structure using Python objects. This allows us to have more consistent, maintainable, and responsive interfaces. 

**Why Use the UI Framework?**
  - Reduced Development Time
  - Consistency in design patterns
  - Reusable Components
  - Extensible and customizable

In today's challenge, we will build on previous knowledge we gained from our Nautobot Views segment to try and gain a better understanding of the Nautobot UI Framework, its components, and how to use it to create object detail views.

We touched a little bit on this topic from [Day 69](../Day069_Nautobot_Views_4_Nautobot_Views_Applying_Theory/) when we converted our `Useful Links` view from the Nautobot Generic `ListView` to `NautobotUIViewSet`. We mentioned [Panels](https://docs.nautobot.com/projects/core/en/stable/development/core/ui-component-framework/#panels), [Tabs](https://docs.nautobot.com/projects/core/en/stable/development/core/ui-component-framework/#panels) and [Buttons](https://docs.nautobot.com/projects/core/en/stable/development/core/ui-component-framework/#buttons) are the main building blocks for the Nautobot UI. One of the common feedback from people new to Django is the initial learning curve of going from 0 to 1 using the framework. In order to get started, we had to learn about creating apps, views, url routing, and some HTML just to see a simple `hello world` to display in our browser. 

That feedback is 100% valid and absolutely true, but the good news is going from 1 to 2 became easier because we front-loaded the learning effort. Things get easier as we become familiar with the pattern. 

This is also true for Nautobot UI Component framework. It takes a bit of learning initially to get things working, however, the work became easier and easier as we use the framework more. 

## Environment Setup

We will use a combination of [Scenario 2](../Lab_Setup/scenario_2_setup/README.md) lab, [https://demo.nautobot.com/](https://demo.nautobot.com/), and [Nautobot Documentation](https://docs.nautobot.com/projects/core/en/latest/user-guide/core-data-model/overview/introduction/) for today's challenge. 

```
$ cd nautobot
$ poetry shell
$ poetry install
$ invoke build
(be patient with this step)
$ invoke debug
(be patient with this step as well)
```

## Code Example

In our Codespace environment, there is already a `ExampleModelUIViewSet` in `example_app` that can be used as a reference for the rest of today's discussion: 

```python file=views.py

class ExampleModelUIViewSet(views.NautobotUIViewSet):
    bulk_update_form_class = forms.ExampleModelBulkEditForm
    filterset_class = filters.ExampleModelFilterSet
    filterset_form_class = forms.ExampleModelFilterForm
    form_class = forms.ExampleModelForm
    queryset = ExampleModel.objects.all()
    serializer_class = serializers.ExampleModelSerializer
    table_class = tables.ExampleModelTable
    object_detail_content = ui.ObjectDetailContent(
        panels=(
            ui.ObjectFieldsPanel(
                section=ui.SectionChoices.LEFT_HALF,
                weight=100,
                fields="__all__",
            ),
            # A table of objects derived dynamically in `get_extra_context()`
            ui.ObjectsTablePanel(
                section=ui.SectionChoices.RIGHT_HALF,
                weight=100,
                context_table_key="dynamic_table",
                max_display_count=3,
            ),
            # A table of non-object data with staticly defined columns
            ui.DataTablePanel(
                section=ui.SectionChoices.RIGHT_HALF,
                label="Custom Table 1 - with dynamic data and hard-coded columns",
                weight=200,
                context_data_key="data_1",
                columns=["col_1", "col_2", "col_3"],
                column_headers=["Column 1", "Column 2", "Column 3"],
            ),
            # A table of non-object data with dynamic (render-time) columns
            ui.DataTablePanel(
                section=ui.SectionChoices.FULL_WIDTH,
                label="Custom Table 2 - with dynamic data and dynamic columns",
                weight=100,
                context_data_key="data_2",
                context_columns_key="columns_2",
                context_column_headers_key="column_headers_2",
            ),
            ui.TextPanel(
                section=ui.SectionChoices.LEFT_HALF,
                label="Text panel with JSON",
                weight=300,
                context_field="text_panel_content",
                render_as=TextPanel.RenderOptions.JSON,
            ),
            ui.TextPanel(
                section=ui.SectionChoices.LEFT_HALF,
                label="Text panel with YAML",
                weight=300,
                context_field="text_panel_content",
                render_as=TextPanel.RenderOptions.YAML,
            ),
            ui.TextPanel(
                section=ui.SectionChoices.RIGHT_HALF,
                label="Text panel with PRE tag usage",
                weight=300,
                context_field="text_panel_code_content",
                render_as=TextPanel.RenderOptions.CODE,
            ),
        ),
    )

    def get_extra_context(self, request, instance):
        context = super().get_extra_context(request, instance)
        if self.action == "retrieve":
            # Add dynamic table of objects for custom panel
            context["dynamic_table"] = CircuitTable(Circuit.objects.restrict(request.user, "view"))
            # Add non-object data for object detail view custom tables
            context["data_1"] = [
                # Because the DataTablePanel defined above specifies the `columns`, col_4 data will not appear
                {"col_1": "value_1a", "col_2": "value_2", "col_3": "value_3", "col_4": "not shown"},
                # Demonstration that null and missing column data is handled safely/correctly
                {"col_1": "value_1b", "col_2": None},
            ]
            # Some more arbitrary data to render
            # Dynamically specify the columns and column_headers for this data table, instead of at declaration time
            context["columns_2"] = ["a", "e", "i", "o", "u"]
            context["column_headers_2"] = ["A", "E", "I", "O", "U"]
            context["data_2"] = [
                {
                    # Column values can include appropriately constructed HTML
                    "a": format_html('<a href="https://en.wikipedia.org/wiki/{val}">{val}</a>', val="a"),
                    # Inappropriately constructed HTML is appropriately escaped on render
                    "e": '<a href="https://example.org/evil-link/e/">e</a>',
                    # Unicode is handled correctly
                    "i": "ℹ︎",  # noqa:RUF001 - intentional letter-like unicode
                    "o": "º",
                    "u": "µ",
                },
                # As above, data not matching a specific `columns` entry will not be rendered
                {"a": 97, "b": 98, "c": 99, "e": 101, "i": 105, "o": 111, "u": 17},
                {"a": "0x61", "b": "0x62", "c": "0x63", "e": "0x65", "i": "0x69", "o": "0x6f", "u": "0x75"},
                {
                    "u": 21 + instance.number,
                    "o": 15 + instance.number,
                    "i": 9 + instance.number,
                    "e": 5 + instance.number,
                    "a": 1 + instance.number,
                },
            ]
            # Add data for TextPanel's
            context["text_panel_content"] = {
                "device_name": "Router1",
                "ip_address": "192.168.1.1",
                "subnet_mask": "255.255.255.0",
                "gateway": "192.168.1.254",
                "interfaces": [
                    {
                        "interface_name": "GigabitEthernet0/0",
                        "ip_address": "10.0.0.1",
                        "subnet_mask": "255.255.255.252",
                        "mac_address": "00:1A:2B:3C:4D:5E",
                    },
                ],
            }
            context["text_panel_code_content"] = 'import abc\nabc()\nprint("Hello world!")'

        return context

    @action(detail=False, name="All Names", methods=["get"], url_path="all-names", url_name="all_names")
    def all_names(self, request):
        """
        Returns a list of all the example model names.
        """
        all_example_models = self.get_queryset()
        return render(
            request,
            "example_app/examplemodel_custom_action_get_all_example_model_names.html",
            {"data": [model.name for model in all_example_models]},
        )

```

Let's begin with reviewing the core concepts. 

## Core Concepts

- **ObjectDetailContent Definition**
  - Define `object_detail_content` attribute for object detail views.
  - Configure for specific data models with Extra Tabs, Panels, and Extra Buttons.

- **Tabs**
  - Major UI building blocks allowing for distinct page content.
  - Support for both client-side toggling and distinct view rendering.

- **Panels**
  - Contain specific content, positioned within sections in a Tab.

- **Buttons**
  - Added to `ObjectDetailContent` for additional functionalities.


Panels are the main container for the UI components, let's see some panel types. 

#### Panel Types

- **Base Panel**

  - Serves as base class for display panels.

  ```python
  from nautobot.apps.ui import Panel, SectionChoices

  Panel(
     weight=100,
     section=SectionChoices.FULL_WIDTH,
     label="Panel Header",
  )
  ```

- **ObjectFieldsPanel**

  - Automatically renders object attributes in a table format.

  ```python
  from nautobot.apps.ui import ObjectFieldsPanel, SectionChoices

  ObjectFieldsPanel(
     weight=100,
     section=SectionChoices.LEFT_HALF,
     label="Object Fields Panel",
     context_object_key="obj",
  )
  ```

- **KeyValueTablePanel**

  - Displays data in a two-column table format.

  ```python
  from nautobot.apps.ui import KeyValueTablePanel

  KeyValueTablePanel(
      weight=100,
      data={
          "speed": "1000000",
          "notes": "**Important**"
      },
  )
  ```

- **GroupedKeyValueTablePanel**

  - Organizes data into collapsible groups.

  ```python
  from nautobot.apps.ui import GroupedKeyValueTablePanel, SectionChoices

  GroupedKeyValueTablePanel(
      weight=300,
      section=SectionChoices.FULL_WIDTH,
      label="Grouped Information",
      body_id="network-details",
      data={
          "Network": {
              "VLAN": "100",
              "IP Range": "192.168.1.0/24"
          },
          "Physical": {
              "Location": "Rack A1",
              "Height": "2U"
          },
          "": {
              "Notes": "Important info"
          }
      },
  )
  ```

- **StatsPanel**

  - Displays statistical information with clickable links to filtered views.

  ```python
  from nautobot.apps.ui import StatsPanel, SectionChoices

  StatsPanel(
      weight=700,
      section=SectionChoices.RIGHT_HALF,
      label="Statistics",
      filter_name="location",
      related_models=[
          Device,
          (Circuit, "circuit_terminations__location__in"),
          (VirtualMachine, "cluster__location__in")
      ],
  )
  ```

- **ObjectTextPanel and TextPanel**

  - Display object attributes and context text in various formats (Markdown, JSON, etc.).

  ```python
  from nautobot.apps.ui import ObjectTextPanel, SectionChoices

  ObjectTextPanel(
     weight=500,
     section=SectionChoices.FULL_WIDTH,
     label="Description",
     object_field="description",
     render_as=ObjectTextPanel.RenderOptions.MARKDOWN,
     render_placeholder=True,
  )
  ```

- **DataTablePanel**

  - Renders tabular data directly from dictionaries.

  ```python
  from nautobot.apps.ui import DataTablePanel

  DataTablePanel(
     weight=100,
     context_data_key="data",
     columns=["one", "two", "three"],
     column_headers=["One", "Two", "Three"]
  )
  ```

- **ObjectsTablePanel**

  - Renders tables of Django model objects with extensive customization.

  ```python
  from nautobot.apps.ui import ObjectsTablePanel, SectionChoices

  ObjectsTablePanel(
      weight=100,
      section=SectionChoices.RIGHT_HALF,
      table_class=ExampleTable,
      table_filter="example_name",
      table_title="Example Table",
  )
  ```

#### Button Types

- **Button**
  - Single button in an object detail view.

  ```python
  from nautobot.apps.ui import Button

  Button(
      weight=100,
      label="Check Secret",
      icon="mdi-test-tube",
      javascript_template_path="extras/secret_check.js",
      attributes={"onClick": "checkSecret()"},
  )
  ```

- **DropdownButton**

  - Contains other buttons rendered as a dropdown menu.

  ```python
  from nautobot.apps.ui import DropdownButton, Button, ButtonColorChoices

  DropdownButton(
      weight=100,
      color=ButtonColorChoices.BLUE,
      label="Add Components",
      icon="mdi-plus-thick",
      required_permissions=["dcim.change_device"],
      children=(
          Button(
              weight=100,
              link_name="dcim:device_consoleports_add",
              label="Console Ports",
              icon="mdi-console",
              required_permissions=["dcim.add_consoleport"],
          ),
          Button(
              weight=200,
              link_name="dcim:device_consoleserverports_add",
              label="Console Server Ports",
              icon="mdi-console-network-outline",
              required_permissions=["dcim.add_consoleserverport"],
          ),
      ),
  )
  ```

## Best Practices

1. **Panel Organization**
   - Use consistent weights, group related information, consider screen sizes.

2. **Performance**
   - Select only needed fields, use `select_related` or `prefetch_related`.

3. **User Experience**
   - Provide clear labels, use consistent patterns, handle errors properly.

4. **Maintenance**
   - Document transformations, update related model lists, use meaningful `body_id` values.

#### Troubleshooting

- **Panels Not Appearing**: Verify section choices, panel weights, data availability.
- **Performance Issues**: Review query complexity, optimize field selections, check database indexes.
- **Layout Problems**: Validate section assignments, review weight ordering, check responsive behavior.
- **Value Rendering**: Verify transform functions, check data types, confirm template paths.

## Resources

- [Transitioning to the UI Component Framework](https://docs.nautobot.com/projects/core/en/stable/development/apps/migration/ui-component-framework/)

- [nautobot.apps.ui](https://docs.nautobot.com/projects/core/en/stable/code-reference/nautobot/apps/ui/)

## Day 74 To Do

Remember to stop the codespace instance on [https://github.com/codespaces/](https://github.com/codespaces/). 

Go ahead and write a post about what you learned from today's challenge on a social media platform of your choice, make sure you use the tag `#100DaysOfNautobot` `#JobsToBeDone` and tag `@networktocode`, so we can share your progress! 

In tomorrow's challenge, we will be dig deeper into Nautobot app navigation menu. See you tomorrow! 

[X/Twitter](<https://twitter.com/intent/tweet?url=https://github.com/nautobot/100-days-of-nautobot&text=I+just+completed+Day+74+of+the+100+days+of+nautobot+challenge+!&hashtags=100DaysOfNautobot,JobsToBeDone>)

[LinkedIn](https://www.linkedin.com/) (Copy & Paste: I just completed Day 74 of 100 Days of Nautobot, https://github.com/nautobot/100-days-of-nautobot-challenge, challenge! @networktocode #JobsToBeDone #100DaysOfNautobot) 
