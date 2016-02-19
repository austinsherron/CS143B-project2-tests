# Test Cases for CS 143B Project 2

# Edge Cases

## Open

+ attempt to open a file that doesn't exist
	+ error
+ attempt to open a file that's already open
	+ error

## Close

+ close a file that doesn't exist
	+ error
+ close a file that isn't open
	+ error

## Seek

+ seek to a position that is >= file length
	+ error
+ seek an index that doesn't exist
	+ error

## Read

+ read an index that doesn't exist
	+ error
+ reading past the end of a file
	+ just read to last available char

## Write

+ write an index that doesn't exist
	+ error
+ writing past max file length
	+ stop writing at max file length

## Create

+ create file that exists
	+ error
+ create file for which there's no more space
	+ error?

## Delete

+ delete file that doesn't exist
	+ error


