#!/usr/bin/python

# Danny Nguyen - LAB 3B
import sys

def splitLists(tempList, numSplit):
    if numSplit <= 0:
        return tempList

    myList = list(tempList)
    for x in range(0, len(myList)):
        for y in range(0, numSplit):
            if not ',' in myList[x]:
                break;
            commaIndex = myList[x].index(',')
            myList[x] = myList[x][commaIndex + 1:]

    return myList

def removeEnds(tempList):
    myList = list(tempList)
    for x in range(0,len(myList)):
        if not ',' in myList[x]:
            break;
        commaIndex= myList[x].index(',')
        myList[x] = myList[x][0:commaIndex]

    return myList

def countFrequency(myList):
    freq = {}
    
    # Check if list is empty
    if not myList:
        return freq

    count = 1;
    value = myList[0];

    for x in range(1, len(myList)):
        if myList[x] != value:
            freq[value] = count
            count = 1
            value = myList[x]
        else:
            count += 1

    freq[value] = count
    return freq



class fileSystemChecker:
    def __init__(self):

        f = open("super.csv",'r')
        self.super = f.readlines()
        f.close()

        f = open("indirect.csv", 'r')
        self.indirect = f.readlines()
        f.close()

        f = open("bitmap.csv", 'r')
        self.bitmap = f.readlines()
        f.close()

        f = open("inode.csv", 'r')
        self.inode = f.readlines()
        f.close()

        f = open("directory.csv", 'r')
        self.dir = f.readlines()
        f.close()

        f = open("group.csv", 'r')
        self.group = f.readlines()
        f.close()




    def checkUnallocatedBlocks(self):
        inode_list = removeEnds(list(self.inode)) # Grabs all used inodes
        list_used_block_nums = splitLists(list(self.inode), 11) # Grabs associated used block numbers

        """ ######### THIS IS TO FIND ALL USED BLOCKS ######### """                
        for x in range(0, len(list_used_block_nums)):
            list_used_block_nums[x] = list_used_block_nums[x].strip()
            list_used_block_nums[x] = list_used_block_nums[x].split(',')

        # Want to create an array of sets
        usedBlocks = []
        for x in range(0, len(list_used_block_nums)):
            blockSet = set()
            for y in range(0, len(list_used_block_nums[x])):
                if list_used_block_nums[x][y] != '0':
                    blockSet.add(int(list_used_block_nums[x][y], 16))
            usedBlocks.append(blockSet)

        """ ######### END ######### """

        """ ######### THIS IS TO FIND ALL FREE BLOCKS ######### """

        bitmaps_list = list(self.bitmap) # Contains copies of all bitmap entries
        bitmaps_list_blocks = removeEnds(bitmaps_list) # This list contains the block numbers of all lines 

        group_list = list(self.group) # Note that group.csv has information about the block number of all inode bitmaps
        group_list = removeEnds(splitLists(group_list, 5)) # Grabs all block bitmap block numbers
        group_set = set()   # Initializes an empty set
        for x in range(0, len(group_list)): # Inserts block bitmap block numbers into set
            group_set.add(group_list[x])

        # Now find all free blocks
        list_of_block_bitmap_entries = [] 
        for x in range(0, len(bitmaps_list_blocks)):
            # If block number of bitmap is a block bitmap
            if bitmaps_list_blocks[x] in group_set:
                # Remove any trailing white spaces
                list_of_block_bitmap_entries.append(bitmaps_list[x].strip())

        list_free_blocks = splitLists(list_of_block_bitmap_entries, 1)
        list_free_blocks = [int(x) for x in list_free_blocks]

        # Now add all free blocks into a set for quick checking
        free_blocks_set = set()
        for x in list_free_blocks:
            free_blocks_set.add(x)

        """ ######### END ######### """


        for x in range(0, len(inode_list)):
            for y in usedBlocks[x]:
                if y in free_blocks_set:
                    print "UNALLOCATED BLOCK < " + str(y) + " > REFERENCED BY INODE < " + inode_list[x] + " > ENTRY <",
                    for z in range(0, len(list_used_block_nums[x])):
                        if y == int(list_used_block_nums[x][z], 16):
                            print str(z) + " >"

    def checkDuplicatelyAllocatedBlock(self):
        inode_list = removeEnds(list(self.inode))
        blockNums = splitLists(list(self.inode), 11)
        for x in range(0, len(blockNums)):
            blockNums[x] = blockNums[x].split(',')

        # Want to create an array of sets
        inodeBlocks = []
        for x in range(0, len(inode_list)):
            blockSet = set()
            for y in range(0, 12):
                if blockNums[x][y] != '0':
                    blockSet.add(int(blockNums[x][y], 16))
            inodeBlocks.append(blockSet)

        # Create a list of lists
        collisions = []
        duplicates = []

        # Map each block number to the inodes that have it
        dictionary = {}

        for x in range(0, len(inodeBlocks)):
            for y in range(x + 1, len(inodeBlocks)):
                for z in inodeBlocks[x]:    # Check each element of the set against the other set
                    if z in inodeBlocks[y]:
                        if z not in duplicates: # check to see if this value already exists
                            duplicates.append(z)
                            tempList = [inode_list[x], inode_list[y]]
                            collisions.append(tempList)
                        else:
                            for w in range(0, len(duplicates)):
                                if duplicates[w] == z:
                                    if inode_list[x] not in collisions[w]:
                                        collisions[w].append(inode_list[x])
                                    if inode_list[y] not in collisions[w]:
                                        collisions[w].append(inode_list[y])

        # For every duplicate value
        for w in range(0, len(duplicates)):
            print "MULTIPLY REFERENCED BLOCK < " + str(duplicates[w]) + " > BY",

            # This specifies how many inodes we'reexpecting to print
            numToPrint = len(collisions[w])

            # For every inode that has this duplicate value
            for x in collisions[w]:    
                # Locates index for the inode we're looking for
                for y in range(0, len(inode_list)):
                    if numToPrint <= 0:
                        break
                    if x == inode_list[y]:
                        # Now find the entry number of the block value
                        for z in range(0, len(blockNums[y])):
                            if numToPrint <= 0:
                                break
                            if duplicates[w] == int(blockNums[y][z], 16):
                                if numToPrint == 1:
                                    print "INODE < " + str(x) + " > " + "ENTRY < " + str(z) + " >"
                                    numToPrint -= 1
                                else:
                                    print "INODE < " + str(x) + " > " + "ENTRY < " + str(z) + " >",
                                    numToPrint -= 1
                        
    def checkUnallocatedInodes(self):
        # Grab inodes of directory
        directoryInodes = list(self.dir)
        directoryInodes = removeEnds(self.dir)
        directoryInodes = [int(x) for x in directoryInodes]

        # Grab entry numbers for each directory
        entry = list(self.dir)
        entry = removeEnds(splitLists(entry, 1))

        # Grab inodes of files within directory
        directoryFileInodes = list(self.dir)
        directoryFileInodes = removeEnds(splitLists(directoryFileInodes, 4))
        directoryFileInodes = [int(x) for x in directoryFileInodes]

        # Grab allocated inodes
        allocatedInodes = list(self.inode)
        allocatedInodes = removeEnds(allocatedInodes)
        allocatedInodes = [int(x) for x in allocatedInodes]

        # Place allocated inodes into a hash set
        inodeSet = set()
        for x in range(0, len(allocatedInodes)):
            inodeSet.add(allocatedInodes[x])

        # Now check each directory file inode to see if it's allocated
        for x in range(0, len(directoryFileInodes)):
            if directoryFileInodes[x] not in inodeSet:
                print "UNALLOCATED INODE < " + str(directoryFileInodes[x]) + " > REFERENCED BY < " + str(directoryInodes[x]) + " > ENTRY < " + entry[x] + " >"

    def checkMissingInode(self):
        inodes_list = list(self.inode)
        bitmaps_list = list(self.bitmap) # Contains copies of all bitmap entries
        bitmaps_list_blocks = removeEnds(bitmaps_list) # This list contains the block numbers of all lines 

        group_list = list(self.group) # Note that group.csv has information about the block number of all inode bitmaps
        group_list = removeEnds(splitLists(group_list, 4)) # Grabs all inode bit map values
        group_set = set()   # Initializes an empty set
        for x in range(0, len(group_list)): # Inserts elements into this set. Allows for quick lookup
            group_set.add(group_list[x])

        # Now find all free inodes
        list_of_inode_bitmap_entries = [] 
        for x in range(0, len(bitmaps_list_blocks)):
            if bitmaps_list_blocks[x] in group_set:
                list_of_inode_bitmap_entries.append(bitmaps_list[x])

        # Place block number and associated inode number in different lists
        inode_bitmap_entries_block = removeEnds(list_of_inode_bitmap_entries)
        inode_bitmap_entries_inode = splitLists(list_of_inode_bitmap_entries, 1)
        inode_bitmap_entries_inode = [int(x) for x in inode_bitmap_entries_inode]

        # List of all used inodes
        takenInodes = removeEnds(inodes_list)
        takenInodes = [int(x) for x in takenInodes]

        # Split each CSV line into its own list
        inodes_list_list = []
        for x in range(0, len(inodes_list)):
            inodes_list_list.append(inodes_list[x].split(','))

        # Removes any white space in any entry within the list of lists
        for x in range(0, len(inodes_list_list)):
            for y in range(0, len(inodes_list_list[x])):
                inodes_list_list[x][y] = inodes_list_list[x][y].strip()

        # This tells us where the free inode should be placed in
        for x in range(0, len(inodes_list_list)):
            freeInode = True;
            if takenInodes[x] < 11: # Inodes 1 - 10 are reserved values
                continue
            else:
                # Test to see if all of this inode's fields are all '0s'
                # Column 1 (file type) does not seem to matter, as it will most likely be a '?'
                for y in range(2, len(inodes_list_list[x])):
                    if inodes_list_list[x][y] != '0':
                        freeInode = False;
                if freeInode:
                    # Now determine which group this inode belongs to
                    if takenInodes[x] < inode_bitmap_entries_inode[x]:
                        print "MISSING INODE < " + str(takenInodes[x]) + " > SHOULD BE IN FREE LIST < " + inode_bitmap_entries_block[x] + " >"
                        break;

    def checkIncorrectLinks(self):
        inodes_list = list(self.inode)

        link_count = list(self.inode)

        dir_list_inodes = list(self.dir)

        inodes_list = removeEnds(inodes_list)
        inodes_list = [int(x) for x in inodes_list]

        link_count = removeEnds(splitLists(link_count, 5))
        link_count = [int(x) for x in link_count]

        dir_list_inodes = removeEnds(splitLists(dir_list_inodes, 4))
        dir_list_inodes = [int(x) for x in dir_list_inodes]

        sorted_dir_list_inodes = sorted(dir_list_inodes, key=int)

        frequency = countFrequency(sorted_dir_list_inodes)

        #for x in range(0, len(link_count)):
            #print link_count[x]
        #for x in range(0, len(dir_list_inodes)):
        #    print sorted_dir_list_inodes[x]

        for x in range(0, len(inodes_list)):
            if link_count[x] != 0:
                actualLinkCount = frequency[inodes_list[x]]
                if actualLinkCount != link_count[x]:
                    print "LINKCOUNT < " + str(inodes_list[x]) + " > IS < " + str(link_count[x]) + " > SHOULD BE < " + str(actualLinkCount) + " >"

        #for x in frequency:
        #    print str(x) + " " + str(frequency[x])

    def checkIncorrectDirectoryEntry(self):
        directory = list(self.dir)
        directory_original = list(self.dir)

        for x in range(0, len(directory)):
            directory[x] = directory[x].strip()
            directory[x] = directory[x].split(',')
            directory_original[x] = directory_original[x].strip()
            directory_original[x] = directory_original[x].split(',')

        # Check the filename to see if it is either '.' or '..'
        for x in reversed(directory):
            if x[5] != "\".\"" and x[5] != "\"..\"":
                directory.remove(x)

        # If entry is ".", have to check to see if both inode values agree
        for x in directory:
            if x[5] == "\".\"":
                if x[0] != x[4]:
                    print "INCORRECT ENTRY IN < " + x[0] + " > NAME < . > LINK TO < " + x[4] + " > SHOULD BE < " + x[0] + " >"
            elif x[5] == "\"..\"":
                # Now need to find parent directory.
                for y in directory_original:
                    # Compare this inode with the file_inode in the original directory
                    if y[5] != "\"..\"" and y[5] != "\".\"" and y[4] == x[0]:
                        if x[4] != y[0]:
                            print "INCORRECT ENTRY IN < " + x[0] + " > NAME < .. > LINK TO < " + x[4] + " > SHOULD BE < " + y[0] + " >"

    def checkInvalidBlockPointer(self):
        blocks = list(self.inode)
        inodes = removeEnds(list(self.inode))
        inodes = [int(x) for x in inodes]

        # Keeps track of indirect file
        ind_blocks = list(self.indirect)

        for x in range(0, len(ind_blocks)):
            ind_blocks[x] = ind_blocks[x].strip()
            ind_blocks[x] = ind_blocks[x].split(',')

        # Converts values from indirect file to integers
        for x in range(0, len(ind_blocks)):
            ind_blocks[x][0] = int(ind_blocks[x][0], 16)
            ind_blocks[x][1] = int(ind_blocks[x][1])
            ind_blocks[x][2] = int(ind_blocks[x][2], 16)

        # Grab contents starting from column of blocks count
        blocks = splitLists(blocks, 10)
        for x in range(0, len(blocks)):
            blocks[x] = blocks[x].strip()
            blocks[x] = blocks[x].split(',')

        # Convert all values to decimal
        for x in range(0, len(blocks)):
            # First value is already in decimal
            blocks[x][0] = int(blocks[x][0])
            for y in range(1, len(blocks[x])):
                blocks[x][y] = int(blocks[x][y], 16)

        # Now determine which blocks are invalid
        for x in range(0, len(blocks)):
            # This is the maximum number of blocks allocated
            count = blocks[x][0]
            for y in range(1, len(blocks[x]) - 3):
                # Invalid block found
                if count <= 0:
                    if blocks[x][y] != 0:
                        # Note that we subtract 1 from y because blocks still contains the column of contained block numbers
                        print "INVALID BLOCK < " + str(blocks[x][y]) + " > IN INODE < " + str(inodes[x]) + " > ENTRY < " + str(y - 1) + " >"
                else:
                    if blocks[x][y] == 0:
                        print "INVALID BLOCK < " + str(blocks[x][y]) + " > IN INODE < " + str(inodes[x]) + " > ENTRY < " + str(y - 1) + " >"
                    count -= 1
            # Now need to analyze indirect file
            if count > 0:
                indirectBlock = blocks[x][13]
                for y in range(0, len(ind_blocks)):
                    if count <= 0:
                        break
                    # Found correct parent block number for indirect block
                    if indirectBlock == ind_blocks[y][0]:
                        if ind_blocks[y][2] == 0:
                            print "INVALID BLOCK < " + str(ind_blocks[y][2]) + " > IN INODE < " + str(inodes[x]) + " > INDIRECT BLOCK < " + str(indirectBlock) + " > ENTRY < " + str(ind_blocks[y][1]) + " >"
                        else:
                            count -= 1




def main():
    sys.stdout = open('lab3b_check.txt', 'w')
    runFiles = fileSystemChecker()
    runFiles.checkUnallocatedBlocks()
    runFiles.checkDuplicatelyAllocatedBlock()
    runFiles.checkUnallocatedInodes()
    runFiles.checkMissingInode()
    runFiles.checkIncorrectLinks()
    runFiles.checkIncorrectDirectoryEntry()
    runFiles.checkInvalidBlockPointer()
    
    

if __name__ == "__main__":
    main()