/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("yh0n4uli0gmuxqq")

  // remove
  collection.schema.removeField("fdjcu6ii")

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("yh0n4uli0gmuxqq")

  // add
  collection.schema.addField(new SchemaField({
    "system": false,
    "id": "fdjcu6ii",
    "name": "audio_file",
    "type": "file",
    "required": false,
    "presentable": false,
    "unique": false,
    "options": {
      "maxSelect": 1,
      "maxSize": 5242880,
      "mimeTypes": [],
      "thumbs": [],
      "protected": false
    }
  }))

  return dao.saveCollection(collection)
})
