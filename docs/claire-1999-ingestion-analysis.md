# Claire 1999 — Ingestion Analysis

## Source folder

```
/Volumes/Nevada/Aperture/20th Century.aplibrary/Masters/1999/Claire
```

28 files total. All are JPEGs from 1999 — no EXIF date metadata (`DateTimeOriginal`,
`CreateDate`) is present in any of them.

The only useful date for these files is the **filesystem modification date** on the originals
in the Aperture library.

---

## Mapping to the database

Files were matched by original filename against the `mappings` table (`Old Name` → `New Name`).

**19 of 28 matched** — these have UUID entries in the database.

**9 of 28 had no mapping entry** — all have `&` or `(` in their filenames. Their ingestion
status is unknown; they cannot be traced to a UUID without a mapping record.

### Unmatched files (no mapping entry)

| Original filename |
|---|
| C&E-990404.jpg |
| C&Eddie-990328.jpg |
| C&Mary(1)-990620.jpg |
| C&Mary(1)-990829.jpg |
| C&Meg(1)-990620.jpg |
| C&Meg(1)-990829.jpg |
| C&Meg(2)-990620.jpg |
| C&Tom&Jenny(1)-990620.jpg |
| Emily&Claire.jpg |

### Matched files — original → UUID

| Original filename | UUID |
|---|---|
| BUNNY1.JPG | 9d17a49c-6c2a-4d8c-a3f3-6c1e308ae4f8.JPG |
| C(1)-990829.jpg | 8b6bed81-0045-4548-8ee3-55c5cced7892.jpg |
| Claire(3)-991203.jpg | f97d536f-e957-42c1-bb26-a83c1773e5c5.jpg |
| Claire(4)-990507.jpg | f0048f90-9f1e-450d-9f59-e35e9584959a.jpg |
| Claire(4)-991203.jpg | 0d3513dd-4c94-43ad-895d-86612341222e.jpg |
| Claire(6)-990507.jpg | 7a9b5420-d86f-4d00-baf5-3e89d2973058.jpg |
| Claire-990328.jpg | f17973af-0b6c-41e1-b8f0-bb493079c4ff.jpg |
| Claire1-990106.jpg | ca1b8d0e-4090-4c85-99a9-5908e9096e57.jpg |
| Claire1.jpg | 14840bc7-5f6b-4fd0-812c-60b48b7dd428.jpg |
| Claire1ed.jpg | ee3ae5a0-7cb4-4518-991e-69cd6926404c.jpg |
| Claire2-990301.jpg | 6ca888e1-67e8-4d00-9b64-93e6ce4b79c9.jpg |
| Claire4-990301.jpg | b08317ff-ba54-42d1-a151-f0f560b146ae.jpg |
| ClaireS.jpg | e5faa162-026d-44bb-974d-3afe34a722cf.jpg |
| Cliare-cake-990620.jpg | a66d9c27-98c5-4a60-8f68-450b4589e8d8.jpg |
| FRAN1.JPG | 177dc283-b575-412f-bd08-5d0c00abda65.JPG |
| FRAN2.JPG | a8db4dd4-79d7-4421-bdcf-b6b5ad1a379f.JPG |
| MegClaire.jpg | b937dfd1-d854-4576-bca7-c67739729c94.jpg |
| claire-990404.jpg | e7ffd7b2-1124-4ac4-ae63-8c5087b7fbbe.jpg |
| claire.jpg | f9877daf-3973-481d-837c-68665b6803a1.jpg |

---

## Date fields in the database

All 19 matched UUIDs were checked against the `exif` table (authoritative source — `exifNoDate`
is a static snapshot and may be incomplete).

**17 of 19** have no date fields populated whatsoever.

**2 of 19** — `ClaireS.jpg` and `MegClaire.jpg` — have only `ProfileDateTime = 1998-02-09T06:49:00`.
This is the creation date of the ICC color profile embedded in the image file, not a
meaningful photo date. (It predates the subject's birth.)

All 19 are effectively undated in the database.

---

## Conclusion

The filesystem dates on the original files in the Aperture library are the only reliable dates
available for these photos. If dates are to be backfilled into the `exif` table, the source
should be `os.path.getmtime()` on the originals, mapped via the `mappings` table.

The 9 unmatched files (filenames containing `&` or `(`) would need to be investigated separately
to determine whether they were ever ingested.
