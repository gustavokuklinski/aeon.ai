# Hello World Plugin for AEON

This is a simple "Hello World" plugin for the AEON system. Its purpose is to demonstrate the basic functionality of creating and integrating a plugin that takes user input and provides a text-based output.

---

## Plugin Structure

The plugin is organized into a single directory that contains its configuration and main script.

```

plugins/
└── hello-world/
    ├── model/
    ├── config.yml
    ├── requirements.txt
    └── main.py

```

---

## Configuration (`config.yml`)

The `config.yml` file defines how this plugin is registered and recognized by the AEON system:

-   **`plugin_name`**: "Hello World Plugin" - A user-friendly name for your plugin.
-   **`type`**: "text-output" - Indicates that this plugin primarily processes text and produces text output.
-   **`command`**: `/hello` - The command users will type into AEON to activate this plugin.
-   **`parameters`**: `<PROMPT>` - Specifies that the `/hello` command expects a single string as an argument.

---

## Usage

To use this plugin, ensure it's placed in the `plugins/` directory of your AEON installation. Once AEON starts, it will automatically load the plugin.

You can then invoke it from the AEON command line like this:

```

/hello This is my message

```

---

## Output

When you run the command, the plugin will echo back the string you provided. For the example above, the output would be:

```

[INFO] 'Hello World Plugin' received input: 'This is my message'
[SUCCESS] Hello, you said: This is my message

```

