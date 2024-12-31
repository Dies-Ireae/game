# OSS Commands for Hierarchical Room Management in Evennia

## Overview

This document provides an explanation of a set of commands designed for managing hierarchical room structures (Districts, Sectors, Neighborhoods, and Sites) within the Evennia MUD framework. These commands enable users to efficiently create and organize complex in-game environments.

## Commands

### 1. **CmdShowHierarchy**
   - **Command:** `+ossmenu/showhierarchy`
   - **Permissions:** `Builder` or `Admin`
   - **Category:** `OSS`
   - **Description:** 
     Displays the hierarchical structure of Districts, Sectors, and Neighborhoods in a tree format.
   - **Usage:**
     ```plaintext
     +ossmenu/showhierarchy
     ```

### 2. **CmdOssSetSector**
   - **Command:** `+oss/setsector <district_name>`
   - **Permissions:** `Builder` or `Immortal`
   - **Category:** `OSS`
   - **Description:** 
     Sets the current room as a Sector under the specified District. If the room is already set as another type, the command returns an error.
   - **Usage:**
     ```plaintext
     +oss/setsector <district_name>
     ```

### 3. **CmdOssSetNeighborhood**
   - **Command:** `+oss/setneighborhood <sector_name>`
   - **Permissions:** `Builder` or `Immortal`
   - **Category:** `OSS`
   - **Description:** 
     Sets the current room as a Neighborhood under the specified Sector. If the room is already set as another type, the command returns an error.
   - **Usage:**
     ```plaintext
     +oss/setneighborhood <sector_name>
     ```

### 4. **CmdOssSetSite**
   - **Command:** `+oss/setsite <neighborhood_name>`
   - **Permissions:** `Builder` or `Immortal`
   - **Category:** `OSS`
   - **Description:** 
     Sets the current room as a Site under the specified Neighborhood. If the room is already set as another type, the command returns an error.
   - **Usage:**
     ```plaintext
     +oss/setsite <neighborhood_name>
     ```

### 5. **CmdOssSetCurrentRoom**
   - **Command:** `+oss/setcurrentroom`
   - **Permissions:** `Builder` or `Immortal`
   - **Category:** `OSS`
   - **Description:** 
     Sets the current room as a sub-location of its parent if the types align correctly.
   - **Usage:**
     ```plaintext
     +oss/setcurrentroom
     ```

### 6. **CmdOssSetDistrict**
   - **Command:** `+oss/setdistrict`
   - **Permissions:** `Builder` or `Immortal`
   - **Category:** `OSS`
   - **Description:** 
     Sets the current room as a District. If the room is already set as another type, the command returns an error.
   - **Usage:**
     ```plaintext
     +oss/setdistrict
     ```

### 7. **CmdSetResolve**
   - **Command:** `+oss/setresolve <value>`
   - **Permissions:** `Builder` or `Immortal`
   - **Category:** `OSS`
   - **Description:** 
     Sets the resolve value of the current room if it is a Neighborhood. This command returns an error if used in a room not designated as a Neighborhood.
   - **Usage:**
     ```plaintext
     +oss/setresolve <value>
     ```

### 8. **CmdSetInfrastructure**
   - **Command:** `+oss/setinfrastructure <value>`
   - **Permissions:** `Builder` or `Immortal`
   - **Category:** `OSS`
   - **Description:** 
     Sets the infrastructure value of the current room if it is a Neighborhood. This command returns an error if used in a room not designated as a Neighborhood.
   - **Usage:**
     ```plaintext
     +oss/setinfrastructure <value>
     ```

### 9. **CmdSetOrder**
   - **Command:** `+oss/setorder <value>`
   - **Permissions:** `Builder` or `Immortal`
   - **Category:** `OSS`
   - **Description:** 
     Sets the order value of the current room if it is a Neighborhood. This command returns an error if used in a room not designated as a Neighborhood.
   - **Usage:**
     ```plaintext
     +oss/setorder <value>
     ```

### 10. **CmdInitializeHierarchy**
   - **Command:** `+oss/init_hierarchy`
   - **Permissions:** `Builder` or `Immortal`
   - **Category:** `OSS`
   - **Description:** 
     Automatically initializes the hierarchy of rooms within the current room. The command sets the immediate sub-rooms as Districts, their children as Sectors, their children as Neighborhoods, and their children as Sites. The command outputs a table showing the actions taken, any warnings, and the structure of the initialized hierarchy.
   - **Usage:**
     ```plaintext
     +oss/init_hierarchy
     ```

## RoomParent Methods

The following methods are expected to be part of the `RoomParent` class. These methods are essential for the functionality of the commands:

- **`set_as_district()`**: Sets the room as a District.
- **`set_as_sector()`**: Sets the room as a Sector.
- **`set_as_neighborhood()`**: Sets the room as a Neighborhood.
- **`set_as_site()`**: Sets the room as a Site.
- **`set_resolve(value)`**: Sets the resolve attribute of the room.
- **`set_infrastructure(value)`**: Sets the infrastructure attribute of the room.
- **`set_order(value)`**: Sets the order attribute of the room.
- **`add_sub_location(room)`**: Adds a sub-location (room) to the current room.

## Installation and Setup

1. **Ensure Evennia is Installed:** These commands are built for the Evennia MUD framework. Ensure that you have a working Evennia setup.
2. **Add Commands:** Integrate these command classes into your Evennia command set. This typically involves adding the command classes to a module and then adding the module to your command settings.
3. **Test the Setup:** Before deploying the commands, test them in a development environment to ensure they work as expected.
