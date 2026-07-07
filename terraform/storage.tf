resource "azurerm_storage_account" "blob" {
  name                     = "blobfatherai007"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"

  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  public_network_access_enabled   = false
}

resource "azurerm_storage_container" "blob" {
  name                  = "documents"
  storage_account_id    = azurerm_storage_account.blob.id
  container_access_type = "private"
}
