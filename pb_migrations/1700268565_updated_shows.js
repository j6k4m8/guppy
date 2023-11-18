/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("lct9kec1bc11rle")

  collection.listRule = ""

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("lct9kec1bc11rle")

  collection.listRule = "@request.auth.id = creator.id"

  return dao.saveCollection(collection)
})
