/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("lct9kec1bc11rle")

  collection.listRule = "@request.auth.id = creator.id"
  collection.viewRule = ""

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("lct9kec1bc11rle")

  collection.listRule = null
  collection.viewRule = null

  return dao.saveCollection(collection)
})
