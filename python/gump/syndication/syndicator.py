              
def syndicate(run):

    #
    # Produce an RSS Feed
    #
    try:    
        from gump.syndication.rss import RSSSyndicator
        simple=RSSSyndicator()
        simple.syndicate(run)    
    except:
        log.error('Failed to generate RSS Feeds', exc_info=1)    
        
    #
    # Produce an Atom Feed
    #
    try:
        from gump.syndication.atom import AtomSyndicator
        atom=AtomSyndicator()
        atom.syndicate(run)
    except:
        log.error('Failed to generate Atom Feeds', exc_info=1)  