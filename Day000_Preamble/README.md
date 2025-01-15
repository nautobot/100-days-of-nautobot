# Preamble

Welcome to the 100 Days of Nautobot Challenge! This is meant to be a fun, self-directed, community-based exercise that can arms you with network automation tools you can use right away.

Each exercise is loosely coupled with each other with very little dependencies by design. They are bite-size challenges that can make the most efficient use of your time in learning.

However, it is always more entertaining and enjoyable to think about these exercises in a real-world scenario. So for the following challenges, they will be loosely centered around a fictitious company called ```Retail-r-Us``` for our examples.  

## Company Overview

Retail-r-Us is a United States retailer with 10 locations on the East Coast and plans to expand to additional locations within the next 12 months.

You are a newly hired network automation engineer tasked with helping Retail-r-Us scale their network for planned upgrades. This journey involves strategic planning and execution to support both current operations and future expansions.

## Locations

- Retailer with 10 locations in the United States East Coast
- 1 HQ Location in NYC
- Expand to 10 more locations on the East Coast and 5 on the West Coast in the next 12 months
- The location design should accommodate future global expansion

## Retail Site Network Designs

- Small sites: single router, single switch, with few wireless Access Points (APs)
- Medium sites: Dual-router, one core switch, few access switches, wireless APs
- Large sites: Dual-router, dual-core switch, access switches, wireless APs
- Remote point of contact at Retail but not full time network engineers

## HQ Site Network Design

- Catalyst switches in L3 mode
- Access Layer switch in MDF Hub-and-Spoke with 10 IDFs
- Cisco DNA Center (DNAC) wireless
- Central network engineering team for design and operations

## Device Consideration

- Meraki is used for retail wireless management
- Cisco Catalyst is used for retail switching
- Branch routers are Cisco ISRs

## Circuits

- Dual providers of ATT & Verizon

## There are several engineering challenges

- Ensure naming standards are being followed
- Ensure network compliance across retail locations
- Automate the following operation tasks due to the level of service desk ticket requests:
  - Bouncing switch port that are attached to IP phones and circuits
  - Change access VLANs on retail switch ports based on device movement
  - Collect output of show commands

 The team have decided to use Nautobot as their source of truth and automation engine.
