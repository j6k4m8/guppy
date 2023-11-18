/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("egg7vh213mo0xqr")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "mmcm8hcv",
    "name": "title",
    "type": "text",
    "required": false,
    "presentable": false,
    "unique": false,
    "options": {
      "min": null,
      "max": null,
      "pattern": ""
    }
  }))

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("egg7vh213mo0xqr")

  // remove
  collection.schema.removeField("mmcm8hcv")

  return dao.saveCollection(collection)
})
