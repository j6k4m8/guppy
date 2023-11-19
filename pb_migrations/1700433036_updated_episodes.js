/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("yh0n4uli0gmuxqq")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "57j58n5k",
    "name": "summary",
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
  const collection = dao.findCollectionByNameOrId("yh0n4uli0gmuxqq")

  // remove
  collection.schema.removeField("57j58n5k")

  return dao.saveCollection(collection)
})
