# Template — LWC Bundle (.html / .js / .js-meta.xml + FLS-aware controller)

The three-file bundle wired to a secure, cacheable Apex controller. See `skills/lwc-component-scaffold`.

## `accountList.html`

```html
<template>
  <lightning-card title="Accounts" icon-name="standard:account">
    <template lwc:if={accounts.data}>
      <template for:each={accounts.data} for:item="acc">
        <p key={acc.Id}>{acc.Name}</p>
      </template>
    </template>
    <template lwc:if={accounts.error}>
      <p class="slds-text-color_error">Could not load accounts.</p>
    </template>
  </lightning-card>
</template>
```

## `accountList.js`

```js
import { LightningElement, wire } from "lwc";
import getAccounts from "@salesforce/apex/AccountListController.getAccounts";

export default class AccountList extends LightningElement {
  // @wire to a cacheable Apex method — preferred over imperative calls
  @wire(getAccounts) accounts;
}
```

## `accountList.js-meta.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<LightningComponentBundle xmlns="http://soap.sforce.com/2006/04/metadata">
  <apiVersion>63.0</apiVersion>
  <isExposed>true</isExposed>
  <targets>
    <target>lightning__AppPage</target>
    <target>lightning__RecordPage</target>
    <target>lightning__HomePage</target>
  </targets>
</LightningComponentBundle>
```

## FLS-aware controller (`AccountListController.cls`)

```apex
public with sharing class AccountListController {
    @AuraEnabled(cacheable=true)
    public static List<Account> getAccounts() {
        return [
            SELECT Id, Name
            FROM Account
            WITH USER_MODE              // enforce CRUD/FLS (v67.0+; pre-v67 use WITH SECURITY_ENFORCED)
            ORDER BY Name
            LIMIT 200
        ];
    }
}
```

Notes: `cacheable=true` for reads; `with sharing` + `WITH USER_MODE`. **At API v67.0+ (Summer '26) `WITH SECURITY_ENFORCED` is removed and no longer compiles — use `WITH USER_MODE`;** on pre-v67.0 classes `WITH SECURITY_ENFORCED` still works. `apiVersion` `[verify-at-build]` against the current release.
