# Forms

The `form` element: JSON settings for one-shot authoring, then PHP actions/validation. Verified against `includes/elements/form.php` + `includes/integrations/form/` (2.3.6).

## Form element JSON

```json
{
  "id": "frm001",
  "name": "form",
  "parent": "con001",
  "children": [],
  "settings": {
    "fields": [
      { "id": "fld1aa", "type": "text",  "label": "Name", "placeholder": "Your name", "required": true, "width": "50" },
      { "id": "fld2bb", "type": "email", "label": "Email", "placeholder": "you@example.com", "required": true, "width": "50" },
      { "id": "fld3cc", "type": "select", "label": "Topic", "options": "Sales\nSupport\nOther", "width": "100" },
      { "id": "fld4dd", "type": "textarea", "label": "Message", "required": true, "width": "100" }
    ],
    "submitButtonText": "Send message",
    "submitButtonStyle": "primary",
    "actions": ["email"],
    "emailSubject": "New inquiry from {{fld1aa}}",
    "emailTo": "admin_email",
    "fromName": "{{fld1aa}}",
    "replyToEmail": "{{fld2bb}}",
    "emailContent": "Name: {{fld1aa}}\nEmail: {{fld2bb}}\nTopic: {{fld3cc}}\n\n{{fld4dd}}",
    "successMessage": "Thanks — we'll reply within one business day.",
    "mailService": "none",
    "showLabels": true
  }
}
```

### Field repeater keys

| Key | Notes |
|-----|-------|
| `id` | 6-char id — referenced as `{{id}}` in email templates and `form-field-{id}` server-side |
| `type` | `text` `email` `textarea` `richtext` `tel` `number` `url` `checkbox` `select` `radio` `file` `image` `gallery` `datepicker` `password` `rememberme` `hidden` `html` |
| `label` / `placeholder` | strings; `showLabels` toggles label display |
| `required` | bool |
| `width` | `"100"`, `"50"`, `"33"` — percent of row |
| `options` | choice types: newline-separated string |
| `value` | default value (hidden fields: dynamic data works — `"{post_id}"`) |
| `min`/`max` | number type |
| `fileUploadLimit`, `fileUploadSize`, `fileUploadAllowedTypes` | file type (`"pdf,jpg"`) |
| `time`/`l10n` | datepicker extras |

### Actions (`actions` array, run in order)

`email` `confirmation-email` `redirect` `webhook` `mailchimp` `sendgrid` `login` `registration` `lost-password` `reset-password` `create-post` `update-post` `save-submission` `custom`

Per-action keys (same settings object): `emailTo` (`admin_email`/`custom` + `emailToCustom`), `emailBcc`, `htmlEmail`, `confirmationEmail*` (To/Subject/Content), `redirectUrl` + `redirectTimeout`, `webhookUrl` + `webhookData`, `registrationRole`, `createPostType`/`createPostTitle`/`createPostStatus`/`createPostMeta`, `saveSubmission` settings.

Spam: `enableRecaptcha` (v3, keys in Bricks settings), `enableHCaptcha`, `enableTurnstile`; honeypot field: add `"isHoneypot": true` to a text field.

Styling: `columns`/`columnGap` (field grid), `field*` keys (`fieldBackgroundColor`, `fieldBorder`, `fieldPadding`, `fieldTypography`…), `label*`, `submitButton*` keys, `placeholderTypography`.

**Login/registration forms:** `actions: ["login"]` with `email`/`password`/`rememberme` fields; the password-protection template form uses a single `password` field.

## PHP: custom action

```php
add_action( 'bricks/form/custom_action', function( $form ) {
    $fields   = $form->get_fields();          // form-field-{id} => value
    $settings = $form->get_settings();
    $email    = $fields['form-field-fld2bb'] ?? '';

    $ok = my_api_call( $email );

    $form->set_result( [
        'type'    => $ok ? 'success' : 'error',
        'message' => $ok ? 'Done!' : 'Something went wrong.',
    ] );
} );
```

Named custom actions: register option via `bricks/elements/form/controls` (add to `$controls['actions']['options']`) and handle `bricks/form/action/{name}`.

## PHP: validation

```php
add_filter( 'bricks/form/validate', function( $errors, $form ) {
    $fields = $form->get_fields();
    $email  = $fields['form-field-fld2bb'] ?? '';

    if ( str_ends_with( $email, '@tempmail.com' ) ) {
        $errors[] = 'Disposable email addresses are not allowed.';
    }
    return $errors;
}, 10, 2 );
```

## PHP: files

```php
add_filter( 'bricks/form/file_directory', fn( $dir, $form, $input ) => $dir, 10, 3 );

add_action( 'bricks/form/custom_action', function( $form ) {
    foreach ( $form->get_uploaded_files() as $field => $files ) {
        foreach ( $files as $file ) {
            // $file['file'] path, $file['url'], $file['type'], $file['name']
        }
    }
} );
```

## Hook reference

```php
add_filter( 'bricks/form/validate', fn( $errors, $form ) => $errors, 10, 2 );
add_filter( 'bricks/form/response', fn( $response, $form ) => $response, 10, 2 );
add_filter( 'bricks/form/email_content', fn( $content, $form, $type ) => $content, 10, 3 ); // type: admin|confirmation
add_filter( 'bricks/form/email_headers', fn( $headers, $form ) => $headers, 10, 2 );
add_filter( 'bricks/form/recaptcha_score_threshold', fn( $score ) => 0.7 );
add_filter( 'bricks/element/form/honeypot/result', fn( $result, $field_id, $form ) => $result, 10, 3 );
add_action( 'bricks/form/custom_action', fn( $form ) => null );
add_action( 'bricks/form/action/{name}', fn( $form ) => null );
```

Form lifecycle: AJAX `bricks_form_submit` → nonce → captcha → honeypot → field validation → file handling → `bricks/form/validate` → actions in order → response. An `error` result from any action stops the chain.

## Interactions

Forms emit `formSubmit` / `formSuccess` / `formError` triggers (`formId: "#brxe-{elementId}"`) — show success blocks, close popups (`action: "hide"`, `target: "popup"`), or fire tracking JS on `formSuccess`.
