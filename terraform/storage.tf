data "azurerm_client_config" "current" {}

resource "azurerm_user_assigned_identity" "storage" {
  name                = "id-blobfather-storage"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_key_vault" "storage" {
  name                          = "kv-blobfather-ai-007"
  location                      = azurerm_resource_group.rg.location
  resource_group_name           = azurerm_resource_group.rg.name
  tenant_id                     = data.azurerm_client_config.current.tenant_id
  sku_name                      = "premium"
  soft_delete_retention_days    = 7
  purge_protection_enabled      = true
  public_network_access_enabled = false

  network_acls {
    bypass         = "AzureServices"
    default_action = "Deny"
  }

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    key_permissions = [
      "Create",
      "Delete",
      "Get",
      "List",
      "Purge",
      "Recover",
      "Update",
    ]
  }

  access_policy {
    tenant_id = azurerm_user_assigned_identity.storage.tenant_id
    object_id = azurerm_user_assigned_identity.storage.principal_id

    key_permissions = [
      "Get",
      "UnwrapKey",
      "WrapKey",
    ]
  }
}

resource "azurerm_key_vault_key" "storage" {
  name            = "blob-storage-key"
  key_vault_id    = azurerm_key_vault.storage.id
  key_type        = "RSA-HSM"
  key_size        = 2048
  expiration_date = "2028-07-07T00:00:00Z"

  key_opts = [
    "decrypt",
    "encrypt",
    "unwrapKey",
    "wrapKey",
  ]
}

resource "azurerm_private_endpoint" "key_vault" {
  name                = "pe-blobfather-key-vault"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.subnet.id

  private_service_connection {
    name                           = "psc-blobfather-key-vault"
    private_connection_resource_id = azurerm_key_vault.storage.id
    subresource_names              = ["vault"]
    is_manual_connection           = false
  }
}

resource "azurerm_storage_account" "blob" {
  name                     = "blobfatherai007"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  account_kind             = "StorageV2"

  min_tls_version                   = "TLS1_2"
  allow_nested_items_to_be_public   = false
  public_network_access_enabled     = false
  shared_access_key_enabled         = false
  infrastructure_encryption_enabled = true

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.storage.id]
  }

  customer_managed_key {
    key_vault_key_id          = azurerm_key_vault_key.storage.id
    user_assigned_identity_id = azurerm_user_assigned_identity.storage.id
  }

  blob_properties {
    delete_retention_policy {
      days = 30
    }

    container_delete_retention_policy {
      days = 30
    }
  }

  queue_properties {
    logging {
      version               = "1.0"
      delete                = true
      read                  = true
      write                 = true
      retention_policy_days = 30
    }
  }

  sas_policy {
    expiration_period = "01.00:00:00"
    expiration_action = "Block"
  }
}

resource "azurerm_storage_container" "blob" {
  # checkov:skip=CKV2_AZURE_21:Modern Azure Monitor diagnostics below replace legacy Storage Insights, which requires Shared Key access.
  name                  = "documents"
  storage_account_id    = azurerm_storage_account.blob.id
  container_access_type = "private"
}

resource "azurerm_log_analytics_workspace" "storage" {
  name                = "log-blobfather-storage"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_monitor_diagnostic_setting" "blob" {
  name                       = "blob-audit-logs"
  target_resource_id         = "${azurerm_storage_account.blob.id}/blobServices/default"
  log_analytics_workspace_id = azurerm_log_analytics_workspace.storage.id

  enabled_log {
    category = "StorageRead"
  }

  enabled_log {
    category = "StorageWrite"
  }

  enabled_log {
    category = "StorageDelete"
  }
}

resource "azurerm_private_endpoint" "storage_blob" {
  name                = "pe-blobfather-storage"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.subnet.id

  private_service_connection {
    name                           = "psc-blobfather-storage"
    private_connection_resource_id = azurerm_storage_account.blob.id
    subresource_names              = ["blob"]
    is_manual_connection           = false
  }
}
