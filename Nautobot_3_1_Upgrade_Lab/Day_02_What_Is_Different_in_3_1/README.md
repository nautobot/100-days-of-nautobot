# Day 2: What's Different in 3.1

Day 1 landed you on Nautobot 3.1.2. This day is a **reference**, not a checklist. As you replay any of the earlier 100 Days against your now-3.1 environment, a few things behave differently. None of them block the lab — Nautobot's migrations did the structural work on Day 1 — but each is worth recognizing so you do not think something is broken.

Eventually Days 1–100 will be re-baselined on 3.1 and these notes will be folded into the per-Day content. Until then, this is the bridge.

## Day017: Job Approvals — Model Renamed

In 3.1, `ScheduledJob.approval_required` is gone. The approval gate now goes through `ApprovalWorkflowStage` objects, and `ScheduledJob.state` tracks the workflow position. The migration in Day 1 populated `state` automatically.

What you will notice when replaying [Day017](../../Day017_Job_Approvals/README.md):

- The "Approval required: yes" label in Day017's screenshots is gone. In 3.1 you will see a workflow-stage card instead.
- The permission you need to grant has changed. `extras.approve_job` is no longer the controlling permission — the new ones are `extras.change_approvalworkflowstage` and `extras.view_approvalworkflowstage`.
- Compare against [demo.nautobot.com](https://demo.nautobot.com/) to see the new approval UI.

**Optional fix-up** (only if you want the Day017 approval gate enforced again): grant the two new permissions to your approver role in Admin → Users → Permissions, then rebuild the workflow stages that mirror your Day017 setup.

> `VERIFY` (live, against your 3.1.2 admin): confirm the exact permission codenames — release notes reference an `ApprovalWorkflowStageDefinition` model and the codename may carry that suffix.

## Day003–Day023: Job Execution Toggles Moved Off the Data Form

`_profile`, `_console_log`, `_job_queue`, and `_ignore_singleton_lock` — if any of your Day003–Day023 jobs put these on the data form — moved to a separate Execution form in 3.1. Jobs that still reference them on the data form keep running, but those toggles silently disappear from the rendered form.

Find any references:

```
$ grep -rn '_profile\|_console_log\|_job_queue\|_ignore_singleton_lock' jobs/
```

**Optional fix-up:** remove the references from the data form. 3.1 surfaces the toggles automatically on the new Execution section, so the cleanup is mechanical.

A new table — `JobConsoleEntry` — captures subprocess `stdout` and `stderr` separately from `JobLogEntry`. You will see both row types in the UI for any job that shells out.

> [!NOTE]
> 3.1 strictly enforces `extras.view_joblogentry`. A user with `view_jobresult` but not `view_joblogentry` can see results but not the log lines. If anyone needs to read job logs, grant the new permission.

## Day015, Day079: REST API and Filter Changes

Two changes affect scripts and saved filters that hit the REST API.

**M2M fields are excluded by default in 3.1**, except `tags`, `content_types`, and `object_types`. The [Day015](../../Day015_Job_API/README.md) examples that read fields like `interface.tagged_vlans` will see those fields missing.

To opt back in, pass `?exclude_m2m=false`:

```
$ curl -H "Authorization: Token $TOKEN" "$BASE/api/dcim/interfaces/?exclude_m2m=false&limit=1" | jq
```

**Several [Day079](../../Day079_Naubotbot_Filter/README.md)-era filters became multi-valued.** A saved filter that used to send `state=active` now needs `state=active&state=pending` (a list). Draft list of affected filters:

- Front Port Templates
- Power Outlets
- Module Bays
- JobLogEntry
- JobResult
- IPAddressToInterface

> `VERIFY` (live, against the 3.1.2 REST API on your Codespace or on [demo.nautobot.com/api/](https://demo.nautobot.com/api/)): confirm the `exclude_m2m` default and the exact multi-value filter list.

## Day080–Day092 Capstone CVE App: Django 5.2 Deprecations

Nautobot 3.1 ships Django 5.2, which dropped a handful of long-deprecated features. If you re-run the [Capstone CVE app](../../Day080_Capstone%20Project%20Part%201_start_working_with_cve_mgmt_app/README.md) on 3.1, you will see these:

- **`Meta.index_together` is removed.** Replace with `indexes = [models.Index(fields=[...])]`, then `makemigrations` / `migrate`.
- **`assertQuerysetEqual` is renamed `assertQuerySetEqual`** (capital S) in test files.
- **The legacy `{% querystring %}` template tag moved.** Update `{% load %}` lines to `nautobot.app.templatetags.legacy_querystring`. Django 5.1+ ships its own built-in `{% querystring %}`, which is what now wins for unqualified `{% load %}`.

These are mechanical fixes — apply them only if you want the Capstone tests to pass cleanly on 3.1.

Other deprecations that still **work** in 3.1 but are slated for removal in 4.0:

- Bootstrap FileStyle
- `django-ajax-tables`
- The old form modal system (replaced by "Embedded Actions")

Not blocking now; flag them when you do a future pass.

## Wrap-Up

These notes will eventually fold into a 3.1-native rewrite of Days 1–100. Until then, treat this Day as the reference you skim when something looks subtly different in your upgraded environment.

The Scenario 1 image is now on the same Nautobot version that backs [demo.nautobot.com](https://demo.nautobot.com/). When in doubt about what 3.1 *should* look like, hit demo as a known-good comparison.

A future expansion pack is planned for popular Nautobot apps that the original 100 Days did not cover (Device Onboarding, Single Source of Truth, others TBD).
