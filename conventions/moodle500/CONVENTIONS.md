# Moodle Plugin Development Conventions

These conventions are used to guide the development of Moodle plugins.

### General

*   **HTTP Requests:** Prefer `httpx` over `requests` for making HTTP requests.
*   **Type Hints:** Use type hints wherever possible to improve code clarity and maintainability.

## Moodle Specific

*   Follow the Moodle coding standards and API documentation:
    *   [Moodle Architecture](https://docs.moodle.org/dev/Moodle_architecture)
    *   [Moodle Development Policies](https://moodledev.io/general/development/policies)
    *   [Moodle Web Service API](https://docs.moodle.org/dev/Web_service_API_functions)

*   Use Moodle's recommended development tools:
    *   [Node.js](https://moodledev.io/general/development/tools/nodejs)

## Moodle Architecture

*   **Modular System:** Moodle is a modular system. Always extend functionality through plugins, not by modifying core files.
*   **Plugin Types:** Understand the different plugin types (activities, resources, blocks, themes, etc.) and use the appropriate APIs for each.
*   **Core Concepts:** Be aware of core Moodle concepts like courses, activities, users, roles, and permissions.
*   **Course Structure:** Courses are sequences of activities and resources grouped into sections.
*   **User Roles:** Users have roles (e.g., student, teacher) that define their capabilities within a course or the site.
*   **Contexts:** Understand that Moodle uses contexts (e.g., courses, modules, blocks) to manage permissions.
*   **Permissions:** Permissions control what users can do in a given context.
*   **Database:** Moodle's database is composed of core tables and plugin-specific tables.
*   **Database Definitions:** Database structure is defined in `install.xml` files within each plugin's `db` folder.
*   **Transaction Script:** Moodle primarily uses a transaction script approach, with core functionality refactored into libraries.
*   **Presentation Layer:** Separate presentation from business logic using themes and renderer classes.
*   **Upgrade Process:** Moodle can be upgraded in four steps:
    1.  Ensure server compatibility.
    2.  Create backups and test installations.
    3.  Replace Moodle code.
    4.  Trigger the upgrade from the admin page.
*   **Activity and Resource Plugins:** Activities and resources are the main tools for teaching and learning.
*   **Block Plugins:** Blocks provide interface functionality on pages.
*   **Theme Plugins:** Themes control the visual style of the Moodle site.
*   **Language Packs:** Moodle is internationalized, use language packs for different languages.
*   **Course Format Plugins:** Course formats control how the course structure is presented.
*   **Authentication Plugins:** Authentication plugins control how users log in.
*   **Enrolment Plugins:** Enrolment plugins control which users are enrolled in which courses.
*   **Repository Plugins:** Repository plugins provide ways for users to get content into Moodle.

## Moodle Development Policies
(from https://moodledev.io/general/development/policies)

These rules are derived from the Moodle development policies and should be followed when developing Moodle plugins.

### General Architecture

*   **Platform Compatibility:** Moodle aims to run on a wide range of platforms. Ensure your code is compatible and portable.
*   **Modularity:** Moodle is modular. Extend functionality through plugins, not by modifying core files.
*   **Plugin Types:** Understand and use the appropriate plugin types (activities, resources, blocks, themes, etc.) and their APIs.

### Coding Style

*   **Consistent Style:** Follow Moodle's coding style to ensure code readability and maintainability.
*   **Community Acceptance:** Adhering to the coding style is important for code to be accepted by the Moodle community.

### Security

*   **Security Guidelines:** Strictly follow Moodle's security guidelines to protect user data and prevent vulnerabilities.
*   **Responsible Internet Citizen:** Ensure your code does not introduce vulnerabilities that could compromise the server.

#### Standards

*   **HTML5 Compliance:** Produce strict, well-formed HTML5 code, preferably backwards compatible with XHTML 1.1.
*   **Accessibility:** Comply with common accessibility guidelines (W3C WCAG 2.0, ARIA).
*   **CSS for Layout:** Use CSS for layout and separate presentation from business logic.
*   **Theme Extension:** If creating a custom theme, extend the Moodle 'Boost' theme.

#### JavaScript

*   **Vanilla JavaScript:** Write new JavaScript in Vanilla JavaScript using ES6 style.
*   **Discourage Frameworks:** Avoid using jQuery, YUI, and other frameworks except for legacy interfaces.
*   **Avoid Interface Manipulation:** Write code to avoid removing or adding interfaces as the page loads.
*   **Accessibility:** Ensure all JavaScript is accessible.

#### Internationalisation

*   **Language Packs:** Keep language strings and locale information separate from the code, using language packs.
*   **Default Language:** Use English (AU) as the default language for all code, comments, and documentation.

#### Accessibility

*   **Wide Range of Users:** Ensure Moodle works well for the widest possible range of people.

#### Component Library

*   **Component Reuse:** Utilize the component library to identify and reuse frequently-used user interface components.

#### Performance

*   **Scalability:** Ensure your code scales well with an increasing number of users, courses, and activities.
*   **Discourage Performance Issues:** Avoid features that are discouraged on production sites for performance reasons.

#### Database

*   **XMLDB:** Use Moodle's database abstraction layer (XMLDB) for database interactions.
*   **Database APIs:** Use the provided tools and APIs for defining, modifying, retrieving, and storing data.

#### Events

*   **Event Observers:** Use event observers to be notified when events happen and act on the data.
*   **Observer Limitations:** Observers cannot modify event data or prevent actions from occurring.
*   **Naming Convention:** Follow the events naming convention.

#### Web Services

*   **Web Service API:** Implement web services according to the Web Service API functions.
*   **Naming Convention:** Follow the naming convention for web service functions.

#### Testing

*   **Manual Testing:** Write clear testing instructions for manual testing.
*   **Unit Testing:** Create automated unit tests for each bit of functionality using PHPUnit.
*   **Acceptance Testing:** Automate user interaction testing using the Behat framework.

#### Third Party Libraries

*   **Standard Inclusion:** Use the standard way to include third-party libraries in your code.

#### Other Standards

*   **Unique Style:** Moodle coding style is unique and not compatible with PEAR or other common PHP standards.

#### Translations

*   **Internationalization:** Pay attention to keeping the language strings and locale information separate from the code, in language packs.

## Bootstrap 5 Migration

These rules are derived from the Bootstrap 5 migration guide and should be followed when updating Moodle's UI.

### General Migration

*   **Gradual Migration:** The migration to Bootstrap 5 will be done in a gradual way, with steps executed in different phases.
*   **PopperJS Upgrade:** Upgrade PopperJS to version 2, while maintaining compatibility with version 1 for Bootstrap 4.
*   **SCSS Deprecation:** Follow the SCSS deprecation process for cleanup after the Bootstrap 5 upgrade.
*   **Refactor BS4 Features:** Refactor Bootstrap 4 features that are deprecated or dropped in Bootstrap 5.
*   **BS5 Bridge:** Use a BS5 "bridge" to address simple breaking changes in advance.
*   **BS5 Upgrade:** Upgrade the current Bootstrap 4 version to version 5.
*   **BS4 Backwards-Compatibility:** Create a backwards-compatibility layer to allow Bootstrap 4 syntax to still work until final deprecation.
*   **Final Deprecation:** Eventually, fully deprecate Bootstrap 4 syntax.

### Refactoring BS4 Features

*   **Badge Colors:** Replace `.badge-*` color classes with background utilities like `.bg-primary` and corresponding text color classes (`.text-dark` or `.text-white`).
*   **Badge Pills:** Replace `.badge-pill` with `.rounded-pill`.
*   **Media Component:** Replace the `.media` component with utility classes like `d-flex`, `flex-shrink-0`, and `flex-grow-1`.
*   **Mixins:** Refactor deprecated mixins such as `hover`, `float-left`, `nav-divider`, `img-retina`, `text-hide`, `invisible`, `form-control-focus`, `text-emphasis-variant`, `size`, `make-container-max-widths`, `g-variant`, and `bg-gradient-variant`. Use the suggested replacements.
*   **Form Groups:** Replace `.form-group` with margin utilities.
*   **Form Inline:** Replace `.form-inline` with utility classes like `d-flex` and `flex-wrap`.
*   **Card Decks:** Replace `.card-deck` with utility classes like `row` and `col`.

### BS5 Bridge

*   **SCSS Bridge File:** Use the `bs5-bridge.scss` file in `theme/boost/scss/moodle` for compatibility changes.
*   **No Gutters:** Replace `.no-gutters` with `.g-0`.
*   **Close Button:** Replace `.close` with `.btn-close`.
*   **Directional Utilities:**
    *   Replace `.float-left` and `.float-right` with `.float-start` and `.float-end`.
    *   Replace `.border-left` and `.border-right` with `.border-start` and `.border-end`.
    *   Replace `.rounded-left` and `.rounded-right` with `.rounded-start` and `.rounded-end`.
    *   Replace `.ml-*` and `.mr-*` with `.ms-*` and `.me-*`.
    *   Replace `.pl-*` and `.pr-*` with `.ps-*` and `.pe-*`.
    *   Replace `.text-left` and `.text-right` with `.text-start` and `.text-end`.
*   **Theme Color Level:** Replace `theme-color-level()` with `shift-color()`, using percentages instead of levels (e.g., level 1 becomes 10%).
*   **Rounded Classes:** Replace `.rounded-sm` and `.rounded-lg` with `.rounded-1` and `.rounded-3`.
*   **Screen Reader Utilities:**
    *   Replace `.sr-only` and `.sr-only-focusable` with `.visually-hidden` and `.visually-hidden-focusable`.
    *   Replace `sr-only()` and `sr-only-focusable()` mixins with `visually-hidden()` and `visually-hidden-focusable()`.
*   **Font Utility Classes:**
    *   Replace `.font-weight-*` with `.fw-*`.
    *   Replace `.font-italic` with `.fst-italic`.

## Aider JavaScript Rules for Moodle Plugin Development

These rules are derived from the Moodle JavaScript guidelines and are intended to guide Aider in generating Moodle-compliant JavaScript code.

#### General

-   **ES2015+ Modules:** All new JavaScript code must use ES2015+ module format, which is transpiled into CommonJS format.
-   **RequireJS Loader:** Modules are loaded in the browser using the RequireJS loader.
-   **Moodle Features:** Use Moodle's Mustache templates, translated strings, and web service framework.
-   **Vanilla JavaScript:** Use vanilla JavaScript with Moodle helpers, avoiding jQuery, YUI, and other frameworks except for legacy interfaces.
-   **Accessibility:** Ensure all JavaScript is accessible.

##### Module Structure

-   **Naming Convention:** JavaScript modules must follow the naming convention: `[component_name]/[optional/sub/namespace/][modulename]`.
-   **Component Directory:** The first directory in any subfolder must be either a Moodle API or `local`.
-   **Examples:**
    -   `mod_forum/discussion`
    -   `mod_assign/grades/grader`
    -   `block_newsitems/local/modal/confirmation`
    -   `core_user/local/participants/selectors`
-   **Subdirectories:** Create a main entry-point module with related modules in a subdirectory.
    -   Example: `core_user/participants` with submodules in `local/participants`.
    -   `local/participants/repository.js` (module name: `core_user/local/participants/repository`)
    -   `local/participants/selectors.js` (module name: `core_user/local/participants/selectors`)
    -   `participants.js` (module name: `core_user/participants`)

##### Module Content

-   **Entry Point:** Each module should have an entry point, usually a function called `init`, which is exported.
-   **Dependencies:** Import dependencies using the `import` keyword.
-   **Exports:** Export functions, objects, classes, and other data structures as needed.

##### DOM Event Handling

-   **Event Listeners:** Use `document.addEventListener()` to listen for DOM events.
-   **CSS Selectors:** Store CSS selectors in a separate `Selectors` object within the module.
-   **Data Attributes:** Use `data-*` attributes to identify elements for event listeners.
-   **Namespaces:** Use namespaces for `data-action` attributes to identify the purpose of the button.
-   **Event Delegation:** Use event delegation to handle events on multiple elements with a single listener.
-   **`e.target.closest()`:** Use `e.target.closest()` to check if the clicked element or its parent matches a CSS selector.

##### Including JavaScript

-   **From Templates:** Use `{{#js}}` tags in Mustache templates to include JavaScript.
    -   Example:
        ```html
        {{#js}}
        require(['mod_forum/discussion'], function(Discussion) {
            Discussion.init();
        });
        {{/js}}
        ```
    -   Use `{{uniqid}}` to generate unique IDs for DOM elements and pass them to the module.
-   **From PHP:** Use `$PAGE->requires->js_call_amd()` to include JavaScript from PHP.
    -   Example: `$PAGE->requires->js_call_amd('mod_forum/discussion', 'init');`
    -   Pass arguments to the function as an array: `$PAGE->requires->js_call_amd('mod_forum/discussion', 'init', [$course->id]);`
    -   Use array destructuring in JavaScript to get named values from multi-dimensional arrays.

##### Data Handling

-   **Data Attributes:** Use `data-*` attributes to pass data to JavaScript modules.
-   **Web Services:** Use Moodle Web Services to fetch complex data structures dynamically.

##### Promises

-   **`then` and `catch`:** Use `then` and `catch` consistently for promise handling.
-   **Return Promises:** Return a Promise from a function if the function is primarily tasked with creating that Promise.
-   **Avoid `done`, `fail`, `always`:** Do not use `done`, `fail`, or `always` functions on Promises.

##### Strings

-   **`core/str` Module:** Use the `core/str` module to fetch and render language strings.
-   **`getString`:** Use `getString` to fetch a single string (returns a native Promise).
-   **`getStrings`:** Use `getStrings` to fetch a set of strings (returns an array of native Promises).
-   **`get_string`:** Use `get_string` to fetch a single string (returns a jQuery Promise, for legacy support).
-   **`get_strings`:** Use `get_strings` to fetch a set of strings (returns an array of jQuery Promises, for legacy support).
-   **Caching:** Strings are cached in LocalStorage.
-   **Native Promises:** Prefer `getString` and `getStrings` from Moodle 4.3 onwards.

##### Prefetching

-   **`core/prefetch` Module:** Use the `core/prefetch` module to prefetch assets.
-   **`prefetchString`:** Prefetch a single string.
-   **`prefetchStrings`:** Prefetch multiple strings.
-   **`prefetchTemplate`:** Prefetch a single template.
-   **`prefetchTemplates`:** Prefetch multiple templates.

##### Dropzone

-   **`core/dropzone` Module:** Use the `core/dropzone` module to create drop zones.
-   **Accessibility:** The module ensures accessibility requirements are met.
-   **Callbacks:** Drop zones trigger callbacks for common actions.

##### Reactive State

-   **Framework Independence:** Core developments are framework independent.
-   **Ad-hoc Library:** Moodle implements a basic reactive state pattern using an ad-hoc library.

##### Tools

-   **NodeJS:** Most Moodle JavaScript tooling requires NodeJS.
-   **Grunt:** Use Grunt to compile JavaScript and CSS, and to lint JavaScript, CSS, and Behat tests.
    -   `npm -g install grunt-cli`
    -   `npx grunt` or `grunt`
-   **ESLint:** Use ESLint for JavaScript linting.

## Aider JavaScript Rules for Moodle AJAX

These rules are derived from the Moodle AJAX guidelines and are intended to guide Aider in generating Moodle-compliant JavaScript code for AJAX interactions.

## General

-   **`core/ajax` Module:** Use the `core/ajax` JavaScript module for all new AJAX interactions.
-   **Web Service API:** AJAX calls should directly call web service functions built using the Moodle Web Service API.
-   **Security:** Web service functions used for AJAX must be marked as available for AJAX in `db/services.php` by defining `'ajax' => true`.
-   **Single HTTP Request:** Multiple web service requests can be chained in a single HTTP request.
-   **Type Checking:** Ensure strict type checking for all parameters and return types in web service functions.

#### Design Patterns

-   **Repository Module:** Place all code using the `core/ajax` module into a single `repository.js` file within the component's `amd/src` directory.
-   **Meaningful Responses:** Each web service call should have a meaningful response.
-   **Chained Calls:** Use `core/ajax` to make multiple web service calls from a single transaction.
-   **Import `call`:** Import the `call` function from `core/ajax` as `fetchMany`.
-   **Export Functions:** Export functions from the repository module that encapsulate specific web service calls.
-   **Call Web Services:** Call the exported functions from other modules to initiate AJAX requests.

#### Key Considerations

-   **Templates:** Use Moodle templates to update parts of the UI in response to AJAX changes.
-   **Theme Context:** When calling `$PAGE->get_renderer()` in a web service, ensure the correct theme is set, potentially by passing the theme as a parameter to the web service.
-   **Text Filtering:** Filter text returned from a web service using `external_format_text` or `external_format_string` with the correct context.
-   **Context Specificity:** Use the most specific context relating to the output when filtering text.
-   **Filter Notification:** After adding dynamic content to a page, notify Moodle's filters via `M.core.event.FILTER_CONTENT_UPDATED`.
-   **Web Service Updates:** After adding or changing any web service definition in `db/services.php`, bump the plugin or Moodle version number and run the upgrade.
-   **Safe Web Services:** Mark web services as safe to call without a session only if they return 100% public information and do not consume many resources.
    -   Add `'loginrequired' => false` to the service definition in `db/services.php`.
    -   Pass `false` as the third argument to the `call` method when calling the web service.

#### Code Examples

### Repository Module

```javascript
import {call as fetchMany} from 'core/ajax';

export const submitGradingForm = (
    assignmentid,
    userid,
    data,
) => fetchMany([{
    methodname: 'mod_assign_submit_grading_form',
    args: {
        assignmentid,
        userid,
        jsonform JSON.stringify(data),
    },
}])[0];
```

### Calling the Web Service

```javascript
import {submitGradingForm} from './repository';

export const doSomething = async() => {
    // ...
    const assignmentId = getAssigmentId();
    const getUserId = getUserId();
    const data = getData();

    const response = await submitGradingForm(assignmentId, userId, data);
    window.console.log(response);
}
```

### Chained Calls

```javascript
import {call as fetchMany} from 'core/ajax';

const getGradingFormRequest = (assignmentid, userid, data) => ({
    methodname: 'mod_assign_submit_grading_form',
    args: {
        assignmentid,
        userid,
        jsonform JSON.stringify(data),
    },
});

const getNextGraderRequest = (assignmentid, userid) => ({
    methodname: 'mod_assign_get_grading_form',
    args: {
        assignmentid,
        userid,
    },
});

export const submitGradingFormAndFetchNext = (
    assignmentId,
    currentUserId,
    currentUserData,
    nextUserId
) => {
    const responses = fetchMany([
        getGradingFormRequest(assignmentId, usecurrentUserIdrId, currentUserData),
        getNextGraderRequest(assignmentId, nextUserId),
    ]);

    return {
        submittedGradingForm: responses[0],
        nextGradingForm: responses[1],
    };
};
```

### Calling Chained Web Services

```javascript
import {submitGradingFormAndFetchNext} from './repository';

export const doSomething = async() => {
    // ...
    const assignmentId = getAssigmentId();
    const getUserId = getUserId();
    const data = getData();

    const {
        submittedGradingForm,
        nextGradingForm,
    } = submitGradingFormAndFetchNext(assignmentId, userId, data, getNextuserId);
    window.console.log(await submittedGradingForm);
    window.console.log(await nextGradingForm);
}
```

## Frankenstyle Component Naming Rules

These rules define how to name components in Moodle, following the "Frankenstyle" convention.

### General Format

Frankenstyle component names are constructed with a prefix and a folder name, separated by an underscore: `prefix_foldername`.

1.  **Prefix:** Determined by the plugin type (e.g., `mod` for activity modules).
2.  **Folder Name:** The plugin's folder name, always in lowercase (e.g., `quiz`).

   Example: The frankenstyle name for the quiz module is `mod_quiz`.

### Plugin Type Prefixes

Refer to the [Plugin types](https://docs.moodle.org/dev/Plugin_types) page for a comprehensive list of plugin types and their corresponding prefixes.

### Core Subsystems

Core subsystems use the format `core_subsystemname`.

Here's a list of core subsystems and their frankenstyle names:

-   Access: `core_access`
-   Administration: `core_admin`
-   Antivirus: `core_antivirus`
-   Authentication: `core_auth`
-   Conditional availability: `core_availability`
-   Backup and restore: `core_backup`
-   Badges: `core_badges`
-   Blocks: `core_block`
-   Blogging: `core_blog`
-   Bulk users operations: `core_bulkusers`
-   Caching: `core_cache`
-   Calendar: `core_calendar`
-   Cohorts: `core_cohort`
-   Comment: `core_comment`
-   Competency based education: `core_competency`
-   Completion: `core_completion`
-   Countries: `core_countries`
-   Course: `core_course`
-   Currencies: `core_currencies`
-   Database transfer: `core_dbtransfer`
-   Debugging: `core_debug`
-   Text editors: `core_editor`
-   Education fields: `core_edufields`
-   Enrol: `core_enrol`
-   Error reporting: `core_error`
-   Favourites: `core_favourites`
-   File picker: `core_filepicker`
-   Files management: `core_files`
-   User filtering: `core_filters`
-   Forms: `core_form`
-   Grades: `core_grades`
-   Advanced grading: `core_grading`
-   Groups: `core_group`
-   Help: `core_help`
-   Hub: `core_hub`
-   IMS CC: `core_imscc`
-   Installer: `core_install`
-   ISO 6392: `core_iso6392`
-   Language pack configuration: `core_langconfig`
-   License: `core_license`
-   Maths library: `core_mathslib`
-   Media: `core_media`
-   Messaging: `core_message`
-   MIME types: `core_mimetypes`
-   MNet: `core_mnet`
-   Dashboard: `core_my`
-   User notes: `core_notes`
-   Page types: `core_pagetype`
-   Pictures and icons: `core_pix`
-   Plagiarism: `core_plagiarism`
-   Plugins management: `core_plugin`
-   Portfolio: `core_portfolio`
-   Privacy: `core_privacy`
-   Course publishing: `core_publish`
-   Question bank engine: `core_question`
-   Ratings: `core_rating`
-   Site registration: `core_register`
-   Repository: `core_repository`
-   RSS: `core_rss`
-   Roles: `core_role`
-   Global search: `core_search`
-   Tabular data display/download (deprecated): `core_table`
-   Tagging: `core_tag`
-   Timezones: `core_timezones`
-   User: `core_user`
-   User key: `core_userkey`
-   Web service: `core_webservice`

### Usage Rules

#### Function Names

-   All plugin functions must start with the full frankenstyle prefix.
-   Activity modules may also use `modulename_` as a prefix for backward compatibility.
-   Avoid global functions; use autoloaded classes instead.

#### Class Names

-   Place all component classes in the `classes` directory.
-   Use namespaces based on the frankenstyle component name.
    -   Example: A discussion class in the forum activity should be in the `mod_forum` namespace and may have a class name of `discussion` - `\mod_forum\discussion`.
-   Avoid non-namespaced classes using only the frankenstyle prefix.

#### Constants

-   All plugin constants must start with an uppercase frankenstyle prefix (e.g., `MOD_FORUM_XXXX`).
-   Use class constants on autoloaded classes instead of global constants where possible.

#### Table Names

-   All table names for a plugin must begin with its frankenstyle name (after the standard Moodle table prefix).
-   Exception: Moodle activities do not have the `mod_` prefix in table names (for historical reasons).
    -   Examples:
        -   `local_coolreport`
        -   `local_coolreport_users`
        -   `forum` (for the `mod_forum` component)

#### Plugin Configuration Table

-   In the `config_plugins` table, the `plugin` column uses the frankenstyle name.

#### Capabilities

-   All capabilities for a plugin use the frankenstyle name, with `/` instead of `_`.
    -   Examples:
        -   `mod/quiz:viewattempt`
        -   `block/library:readbook`

#### Language Files

-   The main language file for each plugin (except activity modules) is named after the frankenstyle component name.
    -   Examples:
        -   `/blocks/participants/lang/en/block_participants.php`
        -   `/mod/quiz/lang/en/quiz.php`

#### Other places

-   `@package` declarations in phpdocs
-   Web service function names
-   Moodle Plugins database
-   JS module names
-   Template names

### Theme Name Variants

-   When creating a theme that is a derivative of another theme, avoid including the parent theme's name in the new theme's name.

### See Also

-   [Plugins](https://docs.moodle.org/dev/Plugins)
-   [Subplugins](https://docs.moodle.org/dev/Subplugins)
-   [Core APIs](https://docs.moodle.org/dev/Core_APIs)
-   [Automatic class loading](https://docs.moodle.org/dev/Automatic_class_loading)
