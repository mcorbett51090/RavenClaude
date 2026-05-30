# Template — Apex Test Class (TestDataFactory, bulk, no SeeAllData)

Bulk-asserting test class. No `SeeAllData=true`; build data with a factory; assert outcomes at 200 records (house opinions #9-#10).

## TestDataFactory

```apex
@isTest
public class TestDataFactory {
    public static List<Account> makeAccounts(Integer count, Boolean doInsert) {
        List<Account> accts = new List<Account>();
        for (Integer i = 0; i < count; i++) {
            accts.add(new Account(Name = 'Test Account ' + i));
        }
        if (doInsert) insert accts;
        return accts;
    }
}
```

## Test class (bulk)

```apex
@isTest
private class AccountTriggerHandlerTest {

    @TestSetup
    static void setup() {
        TestDataFactory.makeAccounts(200, true);   // bulk, not one record
    }

    @isTest
    static void afterUpdate_setsExpectedState_inBulk() {
        List<Account> accts = [SELECT Id FROM Account];
        System.assertEquals(200, accts.size(), 'setup should create 200');

        Test.startTest();
        for (Account a : accts) a.Name = a.Name + ' updated';
        update accts;                  // one DML on the collection
        Test.stopTest();

        // Assert the OUTCOME, never just coverage
        Integer processed = [SELECT COUNT() FROM Account WHERE Archived__c = true];
        System.assertEquals(200, processed, 'all 200 should be processed in bulk');
    }
}
```

Notes: no `@isTest(SeeAllData=true)`; `Test.startTest/stopTest` resets governor limits for the assertion window; assert business outcomes, not row counts of the setup. Aim for ≥75% coverage as a deploy gate, but coverage is not the test.
