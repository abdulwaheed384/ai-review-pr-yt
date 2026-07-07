resource "azurerm_storage_account" "block_storage" {
  name                     = "blobfatherblock007"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Premium"
  account_replication_type = "ZRS"
  account_kind             = "BlockBlobStorage"

  min_tls_version                 = "TLS1_2"
  public_network_access_enabled   = false
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = false

  blob_properties {
    delete_retention_policy {
      days = 30
    }
  }
}

resource "azurerm_storage_container" "blocks" {
  name                  = "block-data"
  storage_account_id    = azurerm_storage_account.block_storage.id
  container_access_type = "private"
}

resource "azurerm_private_endpoint" "block_storage" {
  name                = "pe-blobfather-block"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.subnet.id

  private_service_connection {
    name                           = "psc-blobfather-block"
    private_connection_resource_id = azurerm_storage_account.block_storage.id
    subresource_names              = ["blob"]
    is_manual_connection           = false
  }
}
