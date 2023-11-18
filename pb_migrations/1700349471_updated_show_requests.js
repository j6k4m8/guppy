/// <reference path="../pb_data/types.d.ts" />
migrate((db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("egg7vh213mo0xqr")

  collection.createRule = "@request.auth.id = creator.id && status = \"queued\""

  return dao.saveCollection(collection)
}, (db) => {
  const dao = new Dao(db)
  const collection = dao.findCollectionByNameOrId("egg7vh213mo0xqr")

  collection.createRule = "@request.auth.id = creator.id"

  return dao.saveCollection(collection)
})
