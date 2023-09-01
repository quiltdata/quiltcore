ALGEBRA.md

# KOMD: The Relaxation Algebra

KOMD (pronounced "calmed" or "comedy") stands for:

- Keys
- Objects
- Manifests
- Domains

Specifically, KOMD defines precise semantics for using Keys to register:

1. Objects into Manifests
2. Manifests into Domains

> AK: I think a manifest is actually just a subpath of a domain (namespace)

It is considered an algebra because it can be used to fully describe and reason about any system that conforms to those definitions, independent of the implementation details.  

## Objects

The primary entity in KOMD is the Object, which always has:

- contents
- user metadata (which may be null)
- one or more versions

> AK: consider "zero or more" just to be precise on what can be empty and not

- a unique hash of those versioned contents and metadata
- a universal type
- at least one Key that refers to it
- a parent (which can be an Object or Psuedo-Object, below)

### Keyed Object

Some types of Objects have contents which can be accessed by Keys. These Keyed Objects (or KObjects) could be:

> AK: I don't understand this at all. What makes an object "keyed" the fact that it has a (logical?) key?
> I don't understand how that applies to a SQL table.
> At first I thought it was keyed because there's no contents but that doesn't square with what I see below.
> Do you mean _shallow_ objects?

- Domains
- Manifests
- CSV files
- SQL tables
- etc.

Note that not all Objects are Keyed, but some operations will only work on KObjects.  

### Pseudo-Objects

There are several useful entities that are similar to Objects or KObjects but do not satisfy the above definition.
In particular, Manifests typically use URIs to refer to external storage (object stores, filesystems, databases)
which might not be versioned.
  
We will occasionally refer to these as Pseudo-Objects to emphasize that,
while part of the Algebra, they don't have all the same semantics as true Objects.

## Registration

Registration is the process of creating an _Entry_ for a child Object in a parent KObject that contains:

- a logical Key to identify the Entry
- a physical Key that references the versioned contents of the child Object
- a copy of the associated metadata
- the unique hash for those contents and metadata
- system metadata, such as the child Object's size and type (which might be unknown)

KObjects that supports Registration -- such as Manifests and Domains -- are called Registries.

## Relaxation

- Domains are Registries that are
  a) associated with a specific DataStore and
  b) contain Namespace KObjects that
  c) contain Manifests
- Manifests are Registries with a parent Domain
- The "home" for a Manifest is the parent Domain's DataStore
- A "relaxed Manifest" has all its Entries' physical Keys inside its "home"

> AK: Consider distinguishing "relaxation" relative to a prefix. So something can be relaxed up to s3://,
> up to s3://foo/bar, etc.
> I'm not sure if this is relaxation or containment.

- "Relaxation" is the process of rewriting a "source" Manifest to only use home Keys (including copying over any necessary contents) without changing the hash
- A "neighborly" Manifest has physical keys with the same _type_ of storage as its home (eg, all S3 but different buckets, or all local but different root folders)

## Quality Gates ("Workflows")

- A Domain (or user) can require a Manifest to pass a Quality Gate (sometimes called a "workflow")
- Once a namespace has been assigned (or used with) a Gate, it will always require it
- Gates can require the presence, or particular values, of specific logical Keys or metadata.

> AK: Gates should have nothing to do with domains. We instead need _ex post_ certificates so that
> a) registration never fails (ease of use);
> b) users can talk _about_ packages without modifying the hash
> via README.md, metadata  

If a Gate is required, Manifests are:

1. Pushed and relaxed to the destination Domain (as usual)
2. Registered with a timestamp (numerical Key) under the relevant Namespace (also as usual)
3. However, they are initially assigned a tag (alphabetical Key) of "pending" rather "latest"
4. Only then is the Gate checked
5. If successful, the Manifest is re-tagged as "latest"

> AK: I think relaxation is orthogonal to certification; or relaxation _is_ a certification that certain
> data can attain.

## Merging ChangeSets

In addition to atomically adding and replacing individual Entries, it is possible to apply an entire ChangeSet to a Registry (typically a Manifest).

ChangeSets consist of Operations, which can be thought of all lazy Entries. Operations (which can be either Add or Remove) only resolve to specific content and hashes when "committed." For example, a directory would resolve to a list of files.

> AK: Why not build ChangeSets on true sets so that we can speak of intersection, union, and difference of (keys)
> across sets?

TBD: object-level metadata

- ChangeSets must be created against a specific Namespace, and start out pinned to its "latest" hash. 
- Each Operation keeps track of the hash of its corresponding Entry, if any
- ChangeSets must be "committed" before they can be "applied" to a Manifest
- Applying a ChangeSet atomically fails if any of the Entry hashes do not match

Q: is a committed ChangeSet really a Manifest with a "prior" hash and/or tombstone for each Entry? Does that metadata survive a merge, so we can safely re-merge the resulting Manifest?

Q: can we use a special physical Key (**file:/dev/null**?) as a tombstone within the existing Manifest format?
