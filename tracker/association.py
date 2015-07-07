#!/usr/bin/env python

# TODO --> import from init
import pdb
from sklearn.utils.linear_assignment_ import _hungarian
from tracker import np
from tracker import stats
from tracker import track
from tracker import variables

def normpdf(x, m, v):
    
    return (1 / (np.sqrt(2 * np.pi) * v)) * np.exp(-(1./2) * np.power((x - m) / v, 2))

def lossfunction(tr, sub):

    # Where to create the loss using data from the subject class

    # First simple loss function
    # Based in simple distance to subject base
    (xt, yt), radius = tr.pf.circle
    (xs, ys), radius = sub.circle

    distance = int(np.sqrt(np.power(xt - xs, 2) + np.power(yt - ys, 2)))

    # Second loss function
    # Based in normal probability density function of particles for
    # position and detection size

    (x, y), (h, w), a = sub.rot_box
    p = tr.pf.p
    p_star = tr.pf.p_star
    p_mean = tr.pf.p_mean

    # optimizacion --> no calcular constantemente mean y std, sino hacerlo antes de entrar aqui
    # loss = -x -y -vx -vy
    loss  = - np.log(normpdf(x, np.mean(p[:, 0]), np.std(p[:, 0]))) \
        - np.log(normpdf(y, np.mean(p[:, 1]), np.std(p[:, 1]))) \
        - np.log(normpdf(x - p_star[0], np.mean(p[:, 4]), np.std(p[:, 4]))) \
        - np.log(normpdf(y - p_star[1], np.mean(p[:, 5]), np.std(p[:, 5]))) 
        #- np.log(normpdf(sub.h, np.mean(p[:, 4]), np.std(p[:, 4])))

    debug_flag=0
    if debug_flag:
        """
        print '###'
        print normpdf(p_star[1] - y, np.mean(p[:, 5]), np.std(p[:, 5]))
        print x
        print y
        """
    
        """
        print '----'
        print 'x, y, h: %s, %s, %s' % (x, y, sub.h)
        #print 'x: %s' % - np.log(normpdf(x, np.mean(p[:, 0]), np.std(p[:, 0])))
        print 'vx: %s' % - np.log(normpdf(p_star[0] - x, np.mean(p[:, 4]), np.std(p[:, 4])))
        print 'vy: %s' % - np.log(normpdf(p_star[1] - y, np.mean(p[:, 5]), np.std(p[:, 5]))) 
        print '----'
        """

    return loss, distance


def globallossfunction(tr, sub):

    threshold = 1000

    loss = np.zeros((len(tr), len(sub)))
    distance = np.zeros((len(tr), len(sub)))

    for jj in range(len(tr)):
        for ii in range(len(sub)):
            loss[jj, ii], distance[jj, ii] = lossfunction(tr[jj], sub[ii])

    return loss, distance, threshold


def assignsubjecttonewtrack(sub):

    variables.num_tracks += 1
    tr = track.Track()
    tr.setdefault(sub, variables.num_tracks)
    return tr


def assignsubjecttoexistingtrack(tr, sub):

    tr.updatetrack(sub)
    return tr

def postproc(loss, threshold):

    #print np.isinf(loss)
    #print loss
    #x = np.isinf(loss)
    #print x
    #mask_a = np.all(np.isinf(loss), axis = 1)
    #mask_b = np.all(np.isinf(loss), axis = 0)
    #print mask_a
    #print mask_b

    loss[loss > threshold] = threshold * 2

    return loss

def hungarianassociation(loss, distance, threshold):
    
    debug_flag = 0

    loss = postproc(loss, threshold)

    if debug_flag: print loss

    # SKLEARN association method
    res = _hungarian(loss)
    
    if debug_flag: print res
    
    del_index = []

    for ii in range(len(res)): 
        y, x = res[ii]

        if(loss [y, x] > threshold):
            del_index.append(ii)

    new_res = np.delete(res, del_index, 0)

    if debug_flag: print new_res
    
    return new_res


def getnotassociatedindex(len_sub, len_tr, del_tr, del_sub):

    non_tr = []
    non_sub = []

    non_sub = np.array(range(len_sub))
    non_tr = np.array(range(len_tr))

    non_sub = np.delete(non_sub, del_sub)
    non_tr = np.delete(non_tr, del_tr)

    non_sub = non_sub.tolist()
    non_tr = non_tr.tolist()

    return non_sub, non_tr


def trackmerge(tr, new_tr_copy, non_tr, loss, threshold, res):

    threshold_ = threshold + (2 * threshold / 3)  # margin

    new_tr = new_tr_copy

    for ii in range(len(non_tr)):

        a = loss[non_tr[ii], :]
        b = a[a < threshold_]

        if len(b) > 0:
            if len(b) > 1:
                b = [b.min()]

            # Get merging track overlapped subject's index
            idx_b = np.argwhere(a == b)

            # Get parent track's index
            idx_new_tr = np.argwhere(res[:, 1] == idx_b[0, 0])

            # Merge tracks
            try:  # Maybe wrong hungarian as we expected

                # Only associate locked tracks
                if tr[ii].state is 2 and new_tr[idx_new_tr[0, 0]].state is 2:
                    new_tr[idx_new_tr[0, 0]].associatetrack(tr[ii])
                    tr = np.delete(tr, ii)
                    tr = tr.tolist()

            except:
                pass

    return new_tr, tr


def tracksplit(new_tr, sub, threshold):
    # usage of appareance model might be a good option
    # for distance calculation in this section

    threshold_ = threshold + (2 * threshold / 3)  # margin

    del_idx = []

    for ii in range(len(sub)):
        for tr in new_tr:
            if tr.group and tr.calculatesubjectdistance(sub[ii], threshold_):
                n_tr = tr.deassociatetrack()
                n_tr.updatetrack(sub[ii])
                new_tr.append(n_tr)
                del_idx.append(ii)
                break

    if del_idx:
        sub = np.delete(sub, del_idx)
        sub = sub.tolist()

    return new_tr, sub


def printtracks(tr):

    for t in tr:
        t.printtrack()


def trackupdate(tr, sub, res, loss, threshold):

    new_track = []
    del_index_sub = []
    del_index_tr = []
    init_tr = tr
    init_sub = sub

    # Update successful associations
    for ii in range(len(res)):
        y, x = res[ii]
        new_tr = assignsubjecttoexistingtrack(tr[y], sub[x])
        new_track.append(new_tr)
        del_index_sub.append(x)
        del_index_tr.append(y)

    sub = np.delete(sub, del_index_sub)
    tr = np.delete(tr, del_index_tr)
    sub = sub.tolist()
    tr = tr.tolist()

    # Update missed associations --> where merge should act
    """
    non_index_sub, non_index_tr = getnotassociatedindex(
        len(init_sub), len(init_tr), del_index_tr, del_index_sub)

    new_track, tr = trackmerge(
        tr, new_track, non_index_tr, loss, threshold, res)
    """

    del_index = []

    for ii in range(len(tr)):
        tr[ii].updatetrack()

        # In case track got lost
        if tr[ii].state == 4:
            del_index.append(ii)

    if del_index:
        tr = np.delete(tr, del_index)
        tr = tr.tolist()

    for n in new_track:
        tr.append(n)

    # Update new subjects --> where split should act
    """
    tr, sub = tracksplit(new_track, sub, threshold)
    """
    """
    TODO
    ----
    - Only assign new tracks in outer positions of the image
    """

    for s in sub:
        t = assignsubjecttonewtrack(s)
        tr.append(t)

    return tr


def pfdiffussion(tr):

    new_tr = []

    for t in tr:

        t.pf.pdiffussion()
        new_tr.append(t)

    return new_tr


def pfupdate(tr):

    new_tr = []

    for t in tr:

        t.pf.plikelihood()
        new_tr.append(t)

    return new_tr


def associatetracksubject(tr, sub):

    new_track = []

    # CASES
    # NO tracks
    if not tr:

        for s in sub:

            tr = assignsubjecttonewtrack(s)
            new_track.append(tr)

    # NO detection
    elif not sub:

        for t in tr:
            t.updatemisscount()

        new_track = tr

    # Detection && Tracks present
    else:

        # Particle diffussion
        tr = pfdiffussion(tr)

        # Calculate loss function
        loss, distance, threshold = globallossfunction(tr, sub)

        # Hungarian association
        res = hungarianassociation(loss, distance, threshold)

        # Update tracks with new association
        new_track = trackupdate(tr, sub, res, loss, threshold)

    # Update prob particle filter
    new_track_2 = pfupdate(new_track)

    return new_track_2
