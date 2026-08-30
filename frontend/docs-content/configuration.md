# Configuration and Customization

API Guardian is incredibly powerful out of the box, but true enterprise adoption requires deep customization. We provide extensive configuration options to ensure the platform seamlessly integrates into your existing workflows, coding standards, and operational cadences.

## The `guardian.yml` File
The primary method for configuring API Guardian is via a `guardian.yml` file placed at the root of your connected GitHub repository. If this file is present, our systems will read it during the initialization phase and override the default organization settings.

### Basic Configuration Structure
```yaml
version: 1.0

# Define your primary language and testing framework
runtime:
  language: "node"
  version: "20.x"
  test_command: "npm run test:unit"

# Configure which paths should be ignored by the AST parser
ignore_paths:
  - "tests/fixtures/**"
  - "legacy_app/**"
  - "node_modules/**"

# Configure Pull Request behavior
pull_requests:
  auto_merge: false
  reviewers:
    - "lead-developer"
    - "security-team"
  labels:
    - "api-guardian"
    - "automated-maintenance"
```

## Dashboard Settings
If you prefer not to commit a configuration file to your repository, all of these settings (and more) are available via the interactive Settings interface in the API Guardian dashboard. 

You can configure global defaults for your entire organization, and then override those defaults on a per-repository basis.

## Custom Webhooks and Notifications
Configuration isn't just about code; it's about communication. You can configure precise notification rules. For example:
- Send a Slack message to `#engineering-alerts` when a high-severity Provider Notice is detected.
- Trigger a PagerDuty incident if a critical Guarded API announces an immediate deprecation.
- Send an email digest every Friday summarizing all automated maintenance performed that week.

By tailoring the configuration to your specific needs, API Guardian becomes less of an external tool and more of a native extension of your engineering team.
