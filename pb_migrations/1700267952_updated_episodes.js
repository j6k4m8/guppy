/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("yh0n4uli0gmuxqq")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "ofr5ypd5",
    "name": "show_index",
    "type": "number",
    "required": false,
    "presentable": false,
    "unique": false,
    "options": {
      "min": null,
      "max": null,
      "noDecimal": false
    }
  }))

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("yh0n4uli0gmuxqq")

  // remove
  collection.schema.removeField("ofr5ypd5")

  return dao.saveCollection(collection)
})
