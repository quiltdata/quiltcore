# Refocusing QuiltCore on QuiltSync

cf The [Desktop Sync UX](<https://app.nuclino.com/Quilt-Data/Product-Docs/-DSU-Open-in-Desktop-Desktop-Sync-UX-J22A-b167e48b-d06f-4fd5-b629-f30a2a00b5ec>)

QuiltSync is a tool for synchronizing a local directory with a Quilt package.
We propose refocusing QuiltCore specifically around that use case.
That is, focus on modifying a package by adding, removing, and updating files
from a given local directory, rather than via an API.

The goal is to explicitly ignore all possible corner cases, in favor of ensuring
we ship a solution for that one very narrow, very common use case.

## Key Technologies

### A. UDI: Universal Data Identifier

A UDI is a URI with a "+" in its schema, with well-defined mapping to a dictionary.

### B. `data.yaml`: Universal Data Lineage

The first and best use of `data.yaml` is to associate local folders with remote UDIs,
and the verbs and parameters used to synchronize them.

This allows users (or an app) to simply "push" or "pull" data to/from a remote location,
without having to specify all the other parameters.

### C. Domains:  Bundling Registration and Storage

Domains are the fundamental abstraction for registering and storing data,
as defined by the (evolving) [KOMD Algebra](./ALGEBRA.md).
The initial use cases are S3 Buckets and local filesystems, but the goal
is to eventually extend them to other storage systems, such as Azure Blob Storage,
SharePoint, and even databases.

Importantly:

1. Every Domain has a `data.yaml` file in its root directory.
2. Every subfolder of that Domain is associated with a single remote UDI
3. The registry for that Domain lives in the `.quilt` folder under the root directory

These constraints greatly simplify the management of local state,
allowing us to get a robust MVP out the door.
Later can we worry about allowing greater customization and robustness.

### D. Local `commit` for Manifest creation

The `commit` command creates a new Manifest from a subfolder,
and stores it in the appropriate `.quilt` folder of the parent Domain.
This is why every sync folder must be associated with Domain and its `data.yaml` file,
so the user doesn't have to specify all the extra parameters.

### E. Domain `pull` as the primary sync mechanism

In order to preserve these constraints, each Domain (at least conceptually)
must be responsible for pulling data from a remote location into its local state.
This implies that `push` is actually syntactic sugar for:

1. Find the Domain associated with the local folder
2. Find the remote UDI associated with that folder
3. Create or find the remote Domain for that UDI
4. Tell the remote Domain to pull data (manifest and files) from the local Domain

### F. "Relaxation" to install files alongside Manifests

The entries of an abstract Manifest are defined by their:

- logical keys,
- metadata, and
- hashes of their contents

However, concrete Manifests have explict physical keys.
For example, the physical key for an S3 object is its S3 URI.

Whenever we pull a Manifest into new Domain, we must also pull the files
and rewrite ("relax") the Manifest to use the physical keys of the new Domain.
Thus, both "installation" and "upload" are acutally side-effects from "relaxing"
a "pulled" Manifest.
