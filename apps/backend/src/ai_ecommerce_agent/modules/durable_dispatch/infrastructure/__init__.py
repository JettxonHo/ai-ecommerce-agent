"""Private Durable Dispatch persistence seams.

The SQLAlchemy Core table definition remains private to this infrastructure
package.  Composition code may bind it through an explicit adapter without
widening the Durable Dispatch public facade.
"""
