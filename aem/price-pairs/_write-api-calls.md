# write-api calls — one per payload
Run each with the AEM connector's `write-api` tool, passing your author URL:

## four-k-tv--entry
```
write-api(
  aemUrl: "<your-author-url>",
  code: `
    const body = {"$ref": "aem/price-pairs/four-k-tv--entry.json"};
    return await aem.post('/adobe/sites/cf/fragments/create', body);
  `
)
```

## four-k-tv--premium
```
write-api(
  aemUrl: "<your-author-url>",
  code: `
    const body = {"$ref": "aem/price-pairs/four-k-tv--premium.json"};
    return await aem.post('/adobe/sites/cf/fragments/create', body);
  `
)
```
